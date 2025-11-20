# -- coding: utf-8 --
# Project: object_storage
# Created Date: 2025-05-01
# Author: liming
# Email: lmlala@aliyun.com
# Copyright (c) 2025 FiuAI

import os
import logging
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import oss2
from ..object_storage import ObjectStorage, StorageConfig
from oss2.headers import OSS_OBJECT_TAGGING

logger = logging.getLogger(__name__)

# 设置oss2的日志级别为WARNING，关闭INFO级别的日志
oss2.set_stream_logger(level=logging.WARNING)

class AliCloudStorage(ObjectStorage):
    """阿里云OSS存储实现"""
    
    def __init__(self, config: StorageConfig, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None):
        """初始化阿里云OSS客户端
        
        Args:
            config: 存储配置对象
            auth_tenant_id: 业务租户ID（可为空，后续操作可覆盖）
            auth_company_id: 业务公司ID（可为空，后续操作可覆盖）
            doc_id: 单据ID（可为空，后续操作可覆盖）
        """
        super().__init__(config, auth_tenant_id, auth_company_id, doc_id)
        self.auth = oss2.Auth(config.access_key, config.secret_key)
        self.bucket = oss2.Bucket(
            auth=self.auth,
            endpoint=config.endpoint,
            bucket_name=config.bucket_name
        )
        
    def upload_temp_file(self, object_key: str, data: bytes, meta: Optional[Dict[str, Any]] = None, expires_in: int = 604800, tmppath: str = None) -> bool:
        """上传临时文件到阿里云OSS
        
        Args:
            object_key: 对象存储中的key
            data: 文件数据
            meta: 元数据字典，如果提供则会额外上传 object_key_meta.json 文件
            expires_in: 过期时间（秒），默认604800秒（7天）
            tmppath: 临时文件路径, 如果为空，则使用默认临时目录
        Returns:
            bool: 是否上传成功
        """
        _path = f"{self.config.temp_dir}/{object_key}" if not tmppath else f"{tmppath.rstrip('/')}/{object_key}"
        
        # 计算过期时间戳并设置为元数据
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        expires_timestamp = int(expires_at.timestamp())
        headers = {
            'x-oss-meta-expires-at': str(expires_timestamp),
            'x-oss-meta-expires-in': str(expires_in)
        }
        
        try:
            self.bucket.put_object(_path, data, headers=headers)
            logger.info(f"临时文件上传成功: {_path}, 过期时间: {expires_at.isoformat()}")
            success = True
        except Exception as e:
            logger.error(f"临时文件上传失败: {str(e)}")
            success = False
        
        # 如果有meta，上传meta文件
        if success and meta:
            meta_key = f"{_path}_meta.json"
            try:
                meta_data = json.dumps(meta, ensure_ascii=False).encode('utf-8')
                # meta文件也设置过期时间
                self.bucket.put_object(meta_key, meta_data, headers=headers)
                logger.info(f"元数据文件上传成功: {meta_key}")
            except Exception as e:
                logger.warning(f"元数据文件上传失败: {meta_key}, {str(e)}")
                # meta上传失败不影响主文件上传结果
        
        return success

    def download_temp_file(self, object_key: str, tmppath: str = None) -> Tuple[bytes, Optional[Dict[str, Any]]]:
        """从阿里云OSS下载临时文件
        
        Args:
            object_key: 对象存储中的key
            tmppath: 临时文件路径, 如果为空，则使用默认临时目录
            
        Returns:
            tuple[bytes, Optional[Dict[str, Any]]]: (文件内容, 元数据字典)，文件失败时返回(None, None)，meta读取失败或不存在时返回(文件内容, None)
        """
        _path = f"{self.config.temp_dir}/{object_key}" if not tmppath else f"{tmppath.rstrip('/')}/{object_key}"
        file_data = self.download_file(_path)
        
        # 如果文件下载失败，返回 (None, None)
        if file_data is None:
            return None, None
        
        # 尝试下载meta文件
        meta = None
        meta_key = f"{_path}_meta.json"
        try:
            meta_data = self.download_file(meta_key)
            if meta_data:
                meta = json.loads(meta_data.decode('utf-8'))
                logger.info(f"元数据文件下载成功: {meta_key}")
        except Exception as e:
            logger.debug(f"元数据文件下载失败或不存在: {meta_key}, {str(e)}")
            # meta读取失败不报错，返回None
        
        return file_data, meta

    def upload_file(self, object_key: str, data: bytes) -> bool:
        """上传文件到阿里云OSS
        
        Args:
            object_key: 对象存储中的key
            data: 文件数据
        Returns:
            bool: 是否上传成功
        """
        try:
            self.bucket.put_object(object_key, data)
            logger.info(f"文件上传成功: {object_key}")
            return True
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            return False
            
    def download_file(self, object_key: str) -> bytes:
        """从阿里云OSS下载文件
        
        Args:
            object_key: 对象存储中的key
            
        Returns:
            bytes: 文件内容
        """
        try:
            return self.bucket.get_object(object_key).read()
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            return None
            
    def delete_file(self, object_key: str) -> bool:
        """删除阿里云OSS中的文件
        
        Args:
            object_key: 对象存储中的key
            
        Returns:
            bool: 是否删除成功
        """
        try:
            self.bucket.delete_object(object_key)
            logger.info(f"文件删除成功: {object_key}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            return False
            
    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """列出阿里云OSS中的文件
        
        Args:
            prefix: 文件前缀过滤
            
        Returns:
            List[str]: 文件key列表
        """
        try:
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                files.append(obj.key)
            return files
        except Exception as e:
            logger.error(f"列出文件失败: {str(e)}")
            return [] 

    def _build_doc_path(self, filename: str, auth_tenant_id: Optional[str], auth_company_id: Optional[str], doc_id: Optional[str]) -> str:
        tenant_id = auth_tenant_id or self.auth_tenant_id
        company_id = auth_company_id or self.auth_company_id
        docid = doc_id or self.doc_id
        if not (tenant_id and company_id and docid):
            raise ValueError("auth_tenant_id、auth_company_id、doc_id 不能为空")
        return f"{tenant_id}/{company_id}/{docid}/{filename}"

    def upload_doc_file(self, filename: str, data: bytes, tags: Optional[dict] = None, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None) -> bool:
        try:
            object_key = self._build_doc_path(filename, auth_tenant_id, auth_company_id, doc_id)
            headers = None
            if tags:
                # 构造tagging字符串
                tagging = "&".join([f"{oss2.urlquote(str(k))}={oss2.urlquote(str(v))}" for k, v in tags.items()])
                headers = {OSS_OBJECT_TAGGING: tagging}
            self.bucket.put_object(object_key, data, headers=headers)
            logger.info(f"单据文件上传成功: {object_key}")
            return True
        except Exception as e:
            logger.error(f"单据文件上传失败: {str(e)}")
            return False

    def download_doc_file(self, filename: str, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None) -> bytes:
        try:
            object_key = self._build_doc_path(filename, auth_tenant_id, auth_company_id, doc_id)
            return self.bucket.get_object(object_key).read()
        except Exception as e:
            logger.error(f"单据文件下载失败: {str(e)}")
            return None

    def list_doc_files(self, auth_tenant_id: Optional[str] = None, auth_company_id: Optional[str] = None, doc_id: Optional[str] = None) -> list:
        try:
            tenant_id = auth_tenant_id or self.auth_tenant_id
            company_id = auth_company_id or self.auth_company_id
            docid = doc_id or self.doc_id
            if not (tenant_id and company_id and docid):
                raise ValueError("auth_tenant_id、auth_company_id、doc_id 不能为空")
            prefix = f"{tenant_id}/{company_id}/{docid}/"
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                files.append(obj.key.split(prefix, 1)[-1])
            return files
        except Exception as e:
            logger.error(f"列出单据文件失败: {str(e)}")
            return []

    def generate_presigned_url(self, object_key: str, method: str = "GET", expires_in: int = 3600, 
                              response_headers: Optional[Dict[str, str]] = None,
                              auth_tenant_id: Optional[str] = None, 
                              auth_company_id: Optional[str] = None, 
                              doc_id: Optional[str] = None) -> Optional[str]:
        """
        生成预签名URL
        
        Args:
            object_key: 对象存储中的key
            method: HTTP方法，支持 GET、PUT、POST、DELETE
            expires_in: 过期时间（秒），默认3600秒（1小时）
            response_headers: 响应头设置
            auth_tenant_id: 租户ID（可选，若不传则用实例属性）
            auth_company_id: 公司ID（可选，若不传则用实例属性）
            doc_id: 单据ID（可选，若不传则用实例属性）
            
        Returns:
            Optional[str]: 预签名URL，失败时返回None
        """
        try:
            # 验证参数
            if not object_key:
                raise ValueError("object_key 不能为空")
            
            if method.upper() not in ["GET", "PUT", "POST", "DELETE"]:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            if expires_in <= 0 or expires_in > 604800:  # 最大7天
                raise ValueError("过期时间必须在1秒到604800秒（7天）之间")
            
            # 生成预签名URL
            from datetime import datetime, timedelta
            
            if method.upper() == "GET":
                url = self.bucket.sign_url(
                    method='GET',
                    key=object_key,
                    expires=expires_in,
                    headers=response_headers
                )
            elif method.upper() == "PUT":
                url = self.bucket.sign_url(
                    method='PUT',
                    key=object_key,
                    expires=expires_in
                )
            elif method.upper() == "POST":
                url = self.bucket.sign_url(
                    method='POST',
                    key=object_key,
                    expires=expires_in
                )
            elif method.upper() == "DELETE":
                url = self.bucket.sign_url(
                    method='DELETE',
                    key=object_key,
                    expires=expires_in
                )
            
            logger.info(f"生成预签名URL成功: {object_key}, method: {method}")
            return url
            
        except Exception as e:
            logger.error(f"生成预签名URL失败: {str(e)}")
            return None

    def generate_presigned_doc_url(self, filename: str, method: str = "GET", expires_in: int = 3600,
                                   response_headers: Optional[Dict[str, str]] = None,
                                   auth_tenant_id: Optional[str] = None, 
                                   auth_company_id: Optional[str] = None, 
                                   doc_id: Optional[str] = None) -> Optional[str]:
        """
        生成单据文件的预签名URL
        
        Args:
            filename: 文件名
            method: HTTP方法，支持 GET、PUT、POST、DELETE
            expires_in: 过期时间（秒），默认3600秒（1小时）
            response_headers: 响应头设置
            auth_tenant_id: 租户ID（可选，若不传则用实例属性）
            auth_company_id: 公司ID（可选，若不传则用实例属性）
            doc_id: 单据ID（可选，若不传则用实例属性）
            
        Returns:
            Optional[str]: 预签名URL，失败时返回None
        """
        try:
            # 构建单据文件路径
            object_key = self._build_doc_path(filename, auth_tenant_id, auth_company_id, doc_id)
            
            # 调用通用预签名URL生成方法
            return self.generate_presigned_url(
                object_key=object_key,
                method=method,
                expires_in=expires_in,
                response_headers=response_headers
            )
            
        except Exception as e:
            logger.error(f"生成单据文件预签名URL失败: {str(e)}")
            return None 