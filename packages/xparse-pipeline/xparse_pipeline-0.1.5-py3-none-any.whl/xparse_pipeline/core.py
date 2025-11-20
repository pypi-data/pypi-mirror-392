#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import logging
import requests
import boto3
import json
import uuid
import ftplib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal, Tuple
from dataclasses import dataclass, asdict, field
from pymilvus import MilvusClient
from datetime import datetime

# 设定日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


# ============================================================================
# 配置数据类
# ============================================================================

@dataclass
class ParseConfig:
    """Parse 配置"""
    # 未来可以扩展 parse 相关的配置
    provider: Literal["textin"] = "textin"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)



@dataclass
class ChunkConfig:
    """Chunk 配置"""
    strategy: Literal["basic", "by_title", "by_page"] = "basic"
    include_orig_elements: bool = False
    new_after_n_chars: int = 512
    max_characters: int = 1024
    overlap: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class EmbedConfig:
    """Embed 配置"""
    provider: Literal["qwen", "doubao"] = "qwen"
    model_name: Literal["text-embedding-v3", "text-embedding-v4", "doubao-embedding-large-text-250515", "doubao-embedding-text-240715"] = "text-embedding-v3"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def validate(self) -> None:
        """验证配置"""
        # 支持的 provider 和 model 映射
        provider_models = {
            "qwen": ["text-embedding-v3", "text-embedding-v4"],
            "doubao": ["doubao-embedding-large-text-250515", "doubao-embedding-text-240715"]
        }
        
        if self.provider not in provider_models:
            raise ValueError(f"不支持的 provider: {self.provider}, 支持的有: {list(provider_models.keys())}")
        
        if self.model_name not in provider_models[self.provider]:
            raise ValueError(f"provider '{self.provider}' 不支持模型 '{self.model_name}', 支持的模型: {provider_models[self.provider]}")


@dataclass
class PipelineStats:
    """Pipeline 统计信息"""
    original_elements: int = 0  # 原始解析的元素数量
    chunked_elements: int = 0   # 分块后的元素数量
    embedded_elements: int = 0  # 向量化后的元素数量
    parse_config: Optional[ParseConfig] = None
    chunk_config: Optional[ChunkConfig] = None
    embed_config: Optional[EmbedConfig] = None


# ============================================================================
# 抽象基类
# ============================================================================

class Source(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def list_files(self) -> List[str]:
        """列出所有文件"""
        pass
    
    @abstractmethod
    def read_file(self, file_path: str) -> bytes:
        """读取文件内容"""
        pass


class Destination(ABC):
    """数据目的地抽象基类"""
    
    @abstractmethod
    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        """写入数据"""
        pass


# ============================================================================
# Source 实现类
# ============================================================================

class S3Source(Source):
    """S3/MinIO 数据源"""
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, 
                 bucket: str, prefix: str = '', region: str = 'us-east-1'):
        self.endpoint = endpoint
        self.bucket = bucket
        self.prefix = prefix
        
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=boto3.session.Config(signature_version='s3v4')
        )
        
        # 测试连接
        try:
            self.client.head_bucket(Bucket=bucket)
            print(f"✓ S3 连接成功: {endpoint}/{bucket}")
            logger.info(f"S3 连接成功: {endpoint}/{bucket}")
        except Exception as e:
            print(f"✗ S3 连接失败: {str(e)}")
            raise
    
    def list_files(self) -> List[str]:
        """列出所有文件"""
        files = []
        paginator = self.client.get_paginator('list_objects_v2')
        
        params = {'Bucket': self.bucket}
        if self.prefix:
            params['Prefix'] = self.prefix
        
        for page in paginator.paginate(**params):
            if 'Contents' in page:
                for obj in page['Contents']:
                    if not obj['Key'].endswith('/'):
                        files.append(obj['Key'])
        
        print(f"✓ S3 找到 {len(files)} 个文件")
        return files
    
    def read_file(self, file_path: str) -> bytes:
        """读取文件内容"""
        response = self.client.get_object(Bucket=self.bucket, Key=file_path)
        return response['Body'].read()


class LocalSource(Source):
    """本地文件系统数据源"""
    
    def __init__(self, directory: str, pattern: str = '*'):
        self.directory = Path(directory)
        self.pattern = pattern
        
        if not self.directory.exists():
            raise ValueError(f"目录不存在: {directory}")
        
        print(f"✓ 本地目录: {self.directory}")
        logger.info(f"本地目录: {self.directory}")
    
    def list_files(self) -> List[str]:
        """列出所有文件"""
        files = [str(f.relative_to(self.directory)) 
                for f in self.directory.rglob(self.pattern) 
                if f.is_file()]
        print(f"✓ 本地找到 {len(files)} 个文件")
        return files
    
    def read_file(self, file_path: str) -> bytes:
        """读取文件内容"""
        full_path = self.directory / file_path
        with open(full_path, 'rb') as f:
            return f.read()

class FtpSource(Source):
    """FTP 数据源"""
    
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        
        self.client = ftplib.FTP()
        self.client.connect(self.host, self.port)
        self.client.login(self.username, self.password)

        print(f"✓ FTP 连接成功: {self.host}:{self.port}")
        logger.info(f"FTP 连接成功: {self.host}:{self.port}")
    def list_files(self) -> List[str]:
        """列出所有文件"""
        return self.client.nlst()
    
    def read_file(self, file_path: str) -> bytes:
        """读取文件内容"""
        from io import BytesIO
        buffer = BytesIO()
        self.client.retrbinary(f'RETR {file_path}', buffer.write)
        return buffer.getvalue()


# ============================================================================
# Destination 实现类
# ============================================================================

class MilvusDestination(Destination):
    """Milvus/Zilliz 向量数据库目的地"""
    
    def __init__(self, db_path: str, collection_name: str, dimension: int, api_key: str = None, token: str = None):
        from pymilvus import DataType
        
        self.db_path = db_path
        self.collection_name = collection_name
        self.dimension = dimension
        
        # 创建 MilvusClient，支持 Zilliz 的 API key 或 token
        client_kwargs = {'uri': db_path}
        if api_key:
            client_kwargs['token'] = api_key
        elif token:
            client_kwargs['token'] = token
            
        self.client = MilvusClient(**client_kwargs)
        
        # 检查集合是否存在
        if not self.client.has_collection(collection_name):
            # 使用完整的 Schema 定义创建集合
            schema = self.client.create_schema(
                auto_id=False,
                enable_dynamic_field=True
            )
            
            # 添加字段
            schema.add_field(field_name="element_id", datatype=DataType.VARCHAR, max_length=128, is_primary=True)
            schema.add_field(field_name="embeddings", datatype=DataType.FLOAT_VECTOR, dim=dimension)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="record_id", datatype=DataType.VARCHAR, max_length=128)
            schema.add_field(field_name="metadata", datatype=DataType.JSON)
            
            # 创建索引
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="embeddings",
                index_type="AUTOINDEX",
                metric_type="COSINE"
            )
            
            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )
            print(f"✓ Milvus/Zilliz 集合创建: {collection_name} (自定义 Schema)")
        else:
            print(f"✓ Milvus/Zilliz 集合存在: {collection_name}")
        
        logger.info(f"Milvus/Zilliz 连接成功: {db_path}")
    
    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        """写入数据到 Milvus"""
        try:
            # 转换数据格式
            insert_data = []
            for item in data:
                metadata = item.get('metadata', {})
                if 'embeddings' in item and item['embeddings']:
                    # 获取 element_id（主键），确保不为空
                    element_id = item.get('element_id') or item.get('id') or str(uuid.uuid4())
                    
                    insert_data.append({
                        'embeddings': item['embeddings'],
                        'text': item.get('text', ''),
                        'element_id': element_id,
                        'record_id': metadata.get('record_id', ''),
                        'metadata': metadata,
                        'created_at': datetime.now().isoformat()
                    })
            
            if not insert_data:
                print(f"  ! 警告: 没有有效的向量数据")
                return False
            
            self.client.insert(
                collection_name=self.collection_name,
                data=insert_data
            )
            print(f"  ✓ 写入 Milvus: {len(insert_data)} 条")
            logger.info(f"写入 Milvus 成功: {len(insert_data)} 条")
            return True
        except Exception as e:
            print(f"  ✗ 写入 Milvus 失败: {str(e)}")
            logger.error(f"写入 Milvus 失败: {str(e)}")
            return False


class LocalDestination(Destination):
    """本地文件系统目的地"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ 输出目录: {self.output_dir}")
        logger.info(f"输出目录: {self.output_dir}")
    
    def write(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> bool:
        """写入数据到本地文件"""
        try:
            file_name = metadata.get('file_name', 'output')
            # 移除文件扩展名，添加 .json
            base_name = Path(file_name).stem
            output_file = self.output_dir / f"{base_name}_result.json"
            
            output_data = {
                'metadata': metadata,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ 写入本地: {output_file}")
            logger.info(f"写入本地成功: {output_file}")
            return True
        except Exception as e:
            print(f"  ✗ 写入本地失败: {str(e)}")
            logger.error(f"写入本地失败: {str(e)}")
            return False


# ============================================================================
# Pipeline 核心类
# ============================================================================

class Pipeline:
    """数据处理 Pipeline"""
    
    def __init__(self, 
                 source: Source,
                 destination: Destination,
                 api_base_url: str = 'http://localhost:8000/api/xparse',
                 api_headers: Optional[Dict[str, str]] = None,
                 parse_config: Optional[ParseConfig] = None,
                 chunk_config: Optional[ChunkConfig] = None,
                 embed_config: Optional[EmbedConfig] = None):
        """
        初始化 Pipeline
        
        Args:
            source: 数据源
            destination: 数据目的地
            api_base_url: API 基础 URL
            api_headers: API 请求头
            parse_config: Parse 配置
            chunk_config: Chunk 配置
            embed_config: Embed 配置
        """
        self.source = source
        self.destination = destination
        self.api_base_url = api_base_url.rstrip('/')
        self.api_headers = api_headers or {}
        
        # 配置（使用默认值）
        self.parse_config = parse_config or ParseConfig()
        self.chunk_config = chunk_config or ChunkConfig()
        self.embed_config = embed_config or EmbedConfig()
        
        # 验证 embed 配置
        self.embed_config.validate()
        
        print("=" * 60)
        print("Pipeline 初始化完成")
        print(f"  Parse Config: {self.parse_config}")
        print(f"  Chunk Config: {self.chunk_config}")
        print(f"  Embed Config: {self.embed_config}")
        print("=" * 60)
    
    def _call_pipeline_api(self, file_bytes: bytes, file_name: str) -> Optional[Dict[str, Any]]:
        """
        调用 Pipeline API
        
        Args:
            file_bytes: 文件字节流
            file_name: 原始文件名
        
        Returns:
            API 返回的数据字典（包含 elements 和 stats）
        """
        url = f"{self.api_base_url}/pipeline"
        max_retries = 3
        
        for try_count in range(max_retries):
            try:
                # pipeline 接口使用 multipart/form-data
                files = {'file': (file_name or 'file', file_bytes)}
                form_data = {}
                
                # 构建 stages 数组
                # 新的 API 格式：使用 stages 数组，每个 stage 包含 type 和 config
                stages = [
                    {
                        'type': 'parse',
                        'config': self.parse_config.to_dict()
                    },
                    {
                        'type': 'chunk',
                        'config': self.chunk_config.to_dict()
                    },
                    {
                        'type': 'embed',
                        'config': self.embed_config.to_dict()
                    }
                ]
                
                # 将 stages 转换为 JSON 字符串传递
                form_data['stages'] = json.dumps(stages)
                
                response = requests.post(
                    url,
                    files=files,
                    data=form_data,
                    headers=self.api_headers,
                    timeout=120  # pipeline 需要更长的超时时间
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200 and 'data' in result:
                        return result.get('data')
                    else:
                        return None
                else:
                    print(f"  ! API 错误 {response.status_code}, 重试 {try_count + 1}/{max_retries}")
                    logger.warning(f"API 错误 {response.status_code}: pipeline")
            
            except Exception as e:
                print(f"  ! 请求异常: {str(e)}, 重试 {try_count + 1}/{max_retries}")
                logger.error(f"API 请求异常 pipeline: {str(e)}")
            
            if try_count < max_retries - 1:
                time.sleep(2)
        
        return None
    
    def process_with_pipeline(self, file_bytes: bytes, file_name: str) -> Optional[Tuple[List[Dict[str, Any]], PipelineStats]]:
        """
        使用 pipeline 接口一次性完成所有处理步骤
        
        Args:
            file_bytes: 文件字节流
            file_name: 文件名
        
        Returns:
            (elements, stats) 元组，失败时返回 None
        """
        print(f"  → 调用 Pipeline 接口: {file_name}")
        result = self._call_pipeline_api(file_bytes, file_name)
        
        if result and 'elements' in result and 'stats' in result:
            elements = result['elements']
            stats_data = result['stats']
            
            # 构建 PipelineStats
            stats = PipelineStats(
                original_elements=stats_data.get('original_elements', 0),
                chunked_elements=stats_data.get('chunked_elements', 0),
                embedded_elements=stats_data.get('embedded_elements', 0),
                parse_config=self.parse_config,
                chunk_config=self.chunk_config,
                embed_config=self.embed_config
            )
            
            print(f"  ✓ Pipeline 完成:")
            print(f"    - 原始元素: {stats.original_elements}")
            print(f"    - 分块后: {stats.chunked_elements}")
            print(f"    - 向量化: {stats.embedded_elements}")
            logger.info(f"Pipeline 完成: {file_name}, {stats.embedded_elements} 个向量")
            
            return elements, stats
        else:
            print(f"  ✗ Pipeline 失败")
            logger.error(f"Pipeline 失败: {file_name}")
            return None
    
    def process_file(self, file_path: str) -> bool:
        """
        处理单个文件的完整流程
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否成功
        """
        print(f"\n{'=' * 60}")
        print(f"处理文件: {file_path}")
        logger.info(f"开始处理文件: {file_path}")
        
        try:
            # 1. 读取文件
            print(f"  → 读取文件...")
            file_bytes = self.source.read_file(file_path)
            print(f"  ✓ 文件读取完成: {len(file_bytes)} bytes")
            
            # 2. 使用 pipeline 接口一次性完成所有步骤
            result = self.process_with_pipeline(file_bytes, file_path)
            if not result:
                return False
            
            embedded_data, stats = result
            
            # 3. 写入目的地
            print(f"  → 写入目的地...")
            metadata = {
                'file_name': file_path,
                'total_elements': len(embedded_data),
                'processed_at': datetime.now().isoformat(),
                'stats': {
                    'original_elements': stats.original_elements,
                    'chunked_elements': stats.chunked_elements,
                    'embedded_elements': stats.embedded_elements
                }
            }
            
            success = self.destination.write(embedded_data, metadata)
            
            if success:
                print(f"\n✓✓✓ 文件处理成功: {file_path}")
                logger.info(f"文件处理成功: {file_path}")
            else:
                print(f"\n✗✗✗ 文件处理失败: {file_path}")
                logger.error(f"文件处理失败: {file_path}")
            
            return success
        
        except Exception as e:
            print(f"\n✗✗✗ 处理异常: {str(e)}")
            logger.error(f"处理文件异常 {file_path}: {str(e)}")
            return False
    
    def run(self):
        """运行整个 Pipeline"""
        start_time = time.time()
        
        print("\n" + "=" * 60)
        print("开始执行 Pipeline")
        print("=" * 60)
        logger.info("=" * 60)
        logger.info("开始执行 Pipeline")
        
        # 列出所有文件
        print("\n→ 列出文件...")
        files = self.source.list_files()
        
        if not files:
            print("\n✗ 没有找到文件")
            logger.info("没有找到文件")
            return
        
        # 处理每个文件
        total = len(files)
        success_count = 0
        fail_count = 0
        
        for idx, file_path in enumerate(files, 1):
            print(f"\n进度: [{idx}/{total}]")
            logger.info(f"进度: [{idx}/{total}] - {file_path}")
            
            try:
                if self.process_file(file_path):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                print(f"\n✗✗✗ 文件处理异常: {str(e)}")
                logger.error(f"文件处理异常 {file_path}: {str(e)}")
                fail_count += 1
            
            # 文件间延迟
            if idx < total:
                time.sleep(1)
        
        # 统计信息
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("Pipeline 执行完成！")
        print("=" * 60)
        print(f"总文件数: {total}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"总耗时: {elapsed:.2f} 秒")
        print("=" * 60)
        
        logger.info("=" * 60)
        logger.info(f"Pipeline 完成 - 总数:{total}, 成功:{success_count}, 失败:{fail_count}, 耗时:{elapsed:.2f}秒")
        logger.info("=" * 60)


# ============================================================================
# 配置和启动
# ============================================================================

def create_pipeline_from_config(config: Dict[str, Any]) -> Pipeline:
    """
    根据配置创建 Pipeline
    
    Args:
        config: 配置字典，支持以下字段：
            - source: 数据源配置
            - destination: 目的地配置
            - api_base_url: API 基础 URL
            - api_headers: API 请求头
            - parse_config: Parse 配置（可选）
            - chunk_config: Chunk 配置（可选）
            - embed_config: Embed 配置（可选）
    
    Returns:
        Pipeline 实例
    """
    # 创建 Source
    source_config = config['source']
    if source_config['type'] == 's3':
        source = S3Source(
            endpoint=source_config['endpoint'],
            access_key=source_config['access_key'],
            secret_key=source_config['secret_key'],
            bucket=source_config['bucket'],
            prefix=source_config.get('prefix', ''),
            region=source_config.get('region', 'us-east-1')
        )
    elif source_config['type'] == 'local':
        source = LocalSource(
            directory=source_config['directory'],
            pattern=source_config.get('pattern', '*')
        )
    elif source_config['type'] == 'ftp':
        source = FtpSource(
            host=source_config['host'],
            port=source_config['port'],
            username=source_config['username'],
            password=source_config['password']
        )
    else:
        raise ValueError(f"未知的 source 类型: {source_config['type']}")
    
    # 创建 Destination
    dest_config = config['destination']
    if dest_config['type'] in ['milvus', 'zilliz']:
        destination = MilvusDestination(
            db_path=dest_config['db_path'],
            collection_name=dest_config['collection_name'],
            dimension=dest_config['dimension'],
            api_key=dest_config.get('api_key'),
            token=dest_config.get('token')
        )
    elif dest_config['type'] == 'local':
        destination = LocalDestination(
            output_dir=dest_config['output_dir']
        )
    else:
        raise ValueError(f"未知的 destination 类型: {dest_config['type']}")
    
    # 创建 Parse 配置
    parse_config = None
    if 'parse_config' in config and config['parse_config']:
        parse_config = ParseConfig()  # ParseConfig 目前为空，未来可扩展
    
    # 创建 Chunk 配置
    chunk_config = None
    if 'chunk_config' in config and config['chunk_config']:
        chunk_cfg = config['chunk_config']
        chunk_config = ChunkConfig(
            strategy=chunk_cfg.get('strategy', 'basic'),
            include_orig_elements=chunk_cfg.get('include_orig_elements', False),
            new_after_n_chars=chunk_cfg.get('new_after_n_chars', 512),
            max_characters=chunk_cfg.get('max_characters', 1024),
            overlap=chunk_cfg.get('overlap', 0)
        )
    
    # 创建 Embed 配置
    embed_config = None
    if 'embed_config' in config and config['embed_config']:
        embed_cfg = config['embed_config']
        embed_config = EmbedConfig(
            provider=embed_cfg.get('provider', 'doubao'),
            model_name=embed_cfg.get('model_name', 'text-embedding-v3')
        )
    
    # 创建 Pipeline
    pipeline = Pipeline(
        source=source,
        destination=destination,
        api_base_url=config.get('api_base_url', 'http://localhost:8000/api/xparse'),
        api_headers=config.get('api_headers', {}),
        parse_config=parse_config,
        chunk_config=chunk_config,
        embed_config=embed_config
    )
    
    return pipeline
