"""
AI验证服务客户端

负责与外部AI模型服务通信，提供HTTP客户端、连接池管理、
重试机制和健康检查功能。
"""

import logging
import time
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter

from .data_models import AIInputData, AIValidationResponse, AIServiceConfig
from .exceptions import AIServiceError, AIServiceTimeoutError, AIServiceUnavailableError

logger = logging.getLogger(__name__)


class AIValidationClient:
    """
    AI验证服务客户端

    提供HTTP通信、连接池管理、自动重试和健康检查功能。
    支持配置超时、重试次数和连接池大小。
    """

    def __init__(
        self,
        config: AIServiceConfig,
        pool_connections: int = 10,
        pool_maxsize: int = 30,
    ):
        """
        初始化AI客户端

        Args:
            config: AI服务配置
            pool_connections: 连接池数量
            pool_maxsize: 连接池最大大小
        """
        self.config = config
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.session: Optional[requests.Session] = None
        self._health_status: Optional[bool] = None
        self._last_health_check: Optional[datetime] = None
        self._health_check_interval = timedelta(seconds=30)

        logger.info(
            f"AI客户端初始化完成: {config.endpoint_url}, "
            f"连接池数量: {pool_connections}, "
            f"连接池大小: {pool_maxsize}"
        )

    def _get_session(self) -> requests.Session:
        """
        获取或创建HTTP会话

        使用连接池提高性能，配置超时和请求头。

        Returns:
            requests.Session: HTTP会话对象
        """
        if self.session is None:
            # 创建会话
            self.session = requests.Session()
            
            # 配置连接池
            adapter = HTTPAdapter(
                pool_connections=self.pool_connections,
                pool_maxsize=self.pool_maxsize,
                max_retries=0,  # 手动处理重试
            )
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)

            # 配置请求头
            self.session.headers.update({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}",
                "User-Agent": "OpenFund-AI-Client/1.0",
                **self.config.headers,
            })

            logger.debug("创建新的HTTP会话，连接池已配置")

        return self.session

    def validate_pattern(self, input_data: AIInputData) -> AIValidationResponse:
        """
        调用AI服务进行形态验证

        实现自动重试机制（最多3次），使用指数退避策略。
        处理超时、网络错误和服务不可用等各种错误类型。

        Args:
            input_data: AI输入数据

        Returns:
            AIValidationResponse: AI验证响应

        Raises:
            AIServiceTimeoutError: 服务超时
            AIServiceUnavailableError: 服务不可用
            AIServiceError: 其他服务错误
        """
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(
                    f"调用AI服务，尝试 {attempt + 1}/{self.config.max_retries + 1}"
                )

                start_time = time.time()
                response = self._make_request(input_data)
                elapsed_time = time.time() - start_time

                logger.info(
                    f"AI验证成功，置信度: {response.confidence:.3f}, "
                    f"耗时: {elapsed_time:.2f}秒"
                )
                return response

            except AIServiceTimeoutError as e:
                last_exception = e
                if attempt == self.config.max_retries:
                    logger.error(f"AI服务超时，已达到最大重试次数: {str(e)}")
                    raise

                wait_time = self._calculate_backoff(attempt)
                logger.warning(
                    f"AI服务超时，{wait_time}秒后重试 "
                    f"{attempt + 1}/{self.config.max_retries}"
                )
                time.sleep(wait_time)

            except AIServiceUnavailableError as e:
                last_exception = e
                if attempt == self.config.max_retries:
                    logger.error(f"AI服务不可用，已达到最大重试次数: {str(e)}")
                    raise

                wait_time = self._calculate_backoff(attempt)
                logger.warning(
                    f"AI服务不可用，{wait_time}秒后重试 "
                    f"{attempt + 1}/{self.config.max_retries}"
                )
                time.sleep(wait_time)

            except AIServiceError as e:
                last_exception = e
                # 对于客户端错误（4xx），不重试
                if e.status_code and 400 <= e.status_code < 500:
                    logger.error(f"AI服务客户端错误，不重试: {str(e)}")
                    raise

                if attempt == self.config.max_retries:
                    logger.error(f"AI服务错误，已达到最大重试次数: {str(e)}")
                    raise

                wait_time = self._calculate_backoff(attempt)
                logger.warning(
                    f"AI服务错误，{wait_time}秒后重试 "
                    f"{attempt + 1}/{self.config.max_retries}: {str(e)}"
                )
                time.sleep(wait_time)

            except Exception as e:
                last_exception = e
                logger.error(f"未预期的错误: {str(e)}", exc_info=True)
                if attempt == self.config.max_retries:
                    raise AIServiceError(f"AI服务调用失败: {str(e)}")

                wait_time = self._calculate_backoff(attempt)
                time.sleep(wait_time)

        # 理论上不应该到达这里，但作为保险
        if last_exception:
            raise last_exception
        raise AIServiceError("AI服务调用失败，已达到最大重试次数")

    def _calculate_backoff(self, attempt: int) -> float:
        """
        计算指数退避等待时间

        使用指数退避策略：1秒、2秒、4秒...

        Args:
            attempt: 当前重试次数（从0开始）

        Returns:
            float: 等待时间（秒）
        """
        base_delay = 1.0
        max_delay = 10.0
        delay = min(base_delay * (2**attempt), max_delay)
        return delay

    def _make_request(self, input_data: AIInputData) -> AIValidationResponse:
        """
        发起HTTP请求到AI服务

        处理各种HTTP状态码和网络错误，提供详细的错误信息。

        Args:
            input_data: AI输入数据

        Returns:
            AIValidationResponse: AI验证响应

        Raises:
            AIServiceTimeoutError: 请求超时
            AIServiceUnavailableError: 服务不可用
            AIServiceError: 其他服务错误
        """
        session = self._get_session()

        try:
            # 将输入数据转换为OpenAI格式的请求
            request_data = self._format_openai_request(input_data)

            logger.debug(
                f"发送AI验证请求: {self.config.endpoint_url}, "
                f"交易对: {input_data.market_data.trading_pair}"
            )

            # 发送请求
            response = session.post(
                self.config.endpoint_url,
                json=request_data,
                timeout=self.config.timeout
            )

            # 成功响应
            if response.status_code == 200:
                response_data = response.json()
                return self._parse_openai_response(response_data)

            # 超时相关错误
            elif response.status_code in [408, 504]:
                raise AIServiceTimeoutError(
                    f"AI服务响应超时: HTTP {response.status_code}",
                    timeout_seconds=self.config.timeout,
                )

            # 服务不可用错误（5xx）
            elif response.status_code >= 500:
                error_text = response.text
                raise AIServiceUnavailableError(
                    f"AI服务不可用: HTTP {response.status_code}",
                    status_code=response.status_code,
                    response_data={"error": error_text},
                )

            # 客户端错误（4xx）
            elif response.status_code >= 400:
                error_text = response.text
                error_message = self._parse_error_message(
                    error_text, response.status_code
                )
                raise AIServiceError(
                    error_message,
                    status_code=response.status_code,
                    response_data={"error": error_text},
                )

            # 其他状态码
            else:
                error_text = response.text
                raise AIServiceError(
                    f"AI服务返回未预期状态码: HTTP {response.status_code}",
                    status_code=response.status_code,
                    response_data={"error": error_text},
                )

        except requests.exceptions.Timeout:
            raise AIServiceTimeoutError(
                f"AI服务调用超时: {self.config.timeout}秒",
                timeout_seconds=self.config.timeout,
            )

        except requests.exceptions.ConnectionError as e:
            raise AIServiceUnavailableError(f"无法连接到AI服务: {str(e)}")

        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"网络错误: {str(e)}")

        except AIServiceError:
            # 重新抛出已经处理的异常
            raise

        except Exception as e:
            logger.error(f"请求处理异常: {str(e)}", exc_info=True)
            raise AIServiceError(f"请求处理失败: {str(e)}")

    def _parse_error_message(self, error_text: str, status_code: int) -> str:
        """
        解析错误消息

        Args:
            error_text: 错误文本
            status_code: HTTP状态码

        Returns:
            str: 格式化的错误消息
        """
        error_messages = {
            400: "请求参数错误",
            401: "API密钥无效或未授权",
            403: "访问被拒绝",
            404: "AI服务端点不存在",
            429: "请求频率超限",
        }

        base_message = error_messages.get(status_code, "AI服务返回错误")
        return f"{base_message}: HTTP {status_code} - {error_text[:200]}"

    def _format_openai_request(self, input_data: AIInputData) -> Dict[str, Any]:
        """
        将输入数据格式化为OpenAI兼容的请求格式

        Args:
            input_data: AI输入数据

        Returns:
            Dict[str, Any]: OpenAI格式的请求数据
        """
        # 将市场数据和形态候选转换为文本描述
        data_dict = input_data.to_dict()

        # 构建系统提示
        system_prompt = """你是一个专业的加密货币交易形态分析专家。
你的任务是分析给定的市场数据和形态候选，判断这些形态是否有效，并给出置信度评分。

请以JSON格式返回分析结果，包含以下字段：
- confidence: 置信度评分（0.0-1.0）
- reasoning: 分析推理过程
- feature_importance: 各特征的重要性评分（字典格式）
- processing_time: 处理时间（秒）

示例响应：
{
  "confidence": 0.85,
  "reasoning": "形态点位对齐良好，成交量配合理想，技术指标支持",
  "feature_importance": {
    "price_alignment": 0.9,
    "volume_pattern": 0.8,
    "technical_indicators": 0.7
  },
  "processing_time": 0.5
}"""

        # 构建用户消息
        user_message = f"""请分析以下交易形态：

交易对: {data_dict['trading_pair']}
K线数量: {len(data_dict['candles'])}
形态候选数量: {len(data_dict['patterns'])}

形态详情:
{self._format_patterns_for_prompt(data_dict['patterns'])}

最近K线数据:
{self._format_candles_for_prompt(data_dict['candles'][-20:])}"""

        # 添加机会信息（如果存在）
        if 'additional_features' in data_dict and 'opportunity_info' in data_dict['additional_features']:
            opportunity_info = data_dict['additional_features']['opportunity_info']
            user_message += f"""

交易机会信息:
  目标位: {opportunity_info.get('target_level', 'N/A')}
  止盈目标: {opportunity_info.get('tp_target', 'N/A')}
  形态类型: {opportunity_info.get('equal_points_type', 'N/A')}
  利润距离: {opportunity_info.get('profit_distance', 'N/A')}"""

        user_message += "\n\n请给出你的分析结果（JSON格式）。"

        # 构建OpenAI格式的请求
        return {
            "model": self.config.model_version,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }

    def _format_patterns_for_prompt(self, patterns: List[Dict[str, Any]]) -> str:
        """格式化形态数据为提示文本"""
        result = []
        for i, pattern in enumerate(patterns, 1):
            result.append(f"形态 {i}:")
            result.append(f"  类型: {pattern['type']}")
            result.append(f"  置信度: {pattern['confidence']:.3f}")
            result.append(
                f"  时间范围: {pattern['start_time']} 至 {pattern['end_time']}"
            )
            result.append(f"  关键点数量: {len(pattern['points'])}")
        return "\n".join(result)

    def _format_candles_for_prompt(self, candles: List[Dict[str, Any]]) -> str:
        """格式化K线数据为提示文本"""
        result = []
        for candle in candles[-5:]:  # 只显示最近5根K线
            result.append(
                f"时间: {candle['timestamp']}, "
                f"开: {candle['open']:.2f}, "
                f"高: {candle['high']:.2f}, "
                f"低: {candle['low']:.2f}, "
                f"收: {candle['close']:.2f}, "
                f"量: {candle['volume']:.2f}"
            )
        return "\n".join(result)

    def _parse_openai_response(
        self, response_data: Dict[str, Any]
    ) -> AIValidationResponse:
        """
        解析OpenAI格式的响应

        Args:
            response_data: OpenAI API响应数据

        Returns:
            AIValidationResponse: 解析后的验证响应

        Raises:
            AIServiceError: 解析失败
        """
        try:
            # 从OpenAI响应中提取内容
            if "choices" not in response_data or not response_data["choices"]:
                raise AIServiceError("OpenAI响应缺少choices字段")

            content = response_data["choices"][0]["message"]["content"]

            # 解析JSON内容
            import json

            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError as e:
                logger.warning(f"AI响应不是有效的JSON，尝试提取: {content[:200]}")
                # 如果不是JSON，返回默认值
                parsed_content = {
                    "confidence": 0.5,
                    "reasoning": content,
                    "feature_importance": {},
                    "processing_time": 0.0,
                }

            return AIValidationResponse(
                confidence=parsed_content.get("confidence", 0.0),
                reasoning=parsed_content.get("reasoning", ""),
                feature_importance=parsed_content.get("feature_importance", {}),
                model_version=self.config.model_version,
                processing_time=parsed_content.get("processing_time", 0.0),
                raw_response=response_data,
            )
        except Exception as e:
            logger.error(f"解析OpenAI响应失败: {str(e)}", exc_info=True)
            raise AIServiceError(f"AI响应解析失败: {str(e)}")

    def health_check(self, force: bool = False) -> bool:
        """
        检查AI服务健康状态（OpenAI兼容版本）

        使用缓存机制避免频繁检查，默认缓存30秒。
        由于OpenAI API没有专门的health端点，这里通过发送一个简单的测试请求来检查。

        Args:
            force: 是否强制检查，忽略缓存

        Returns:
            bool: 服务是否健康
        """
        # 检查缓存
        if not force and self._health_status is not None and self._last_health_check:
            if datetime.now() - self._last_health_check < self._health_check_interval:
                logger.debug(f"使用缓存的健康状态: {self._health_status}")
                return self._health_status

        try:
            session = self._get_session()

            logger.debug(f"执行AI服务健康检查: {self.config.endpoint_url}")

            # 发送一个简单的测试请求
            test_request = {
                "model": self.config.model_version,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5,
            }

            # 使用较短的超时时间进行健康检查
            response = session.post(
                self.config.endpoint_url,
                json=test_request,
                timeout=5
            )
            
            is_healthy = response.status_code == 200

            if is_healthy:
                logger.info("AI服务健康检查通过")
            else:
                logger.warning(f"AI服务健康检查失败: HTTP {response.status_code}")

            # 更新缓存
            self._health_status = is_healthy
            self._last_health_check = datetime.now()

            return is_healthy

        except requests.exceptions.Timeout:
            logger.warning("AI服务健康检查超时")
            self._health_status = False
            self._last_health_check = datetime.now()
            return False

        except requests.exceptions.ConnectionError as e:
            logger.warning(f"AI服务健康检查连接失败: {str(e)}")
            self._health_status = False
            self._last_health_check = datetime.now()
            return False

        except Exception as e:
            logger.warning(f"AI服务健康检查失败: {str(e)}")
            self._health_status = False
            self._last_health_check = datetime.now()
            return False

    def get_service_info(self) -> Dict[str, Any]:
        """
        获取AI服务信息（OpenAI兼容版本）

        OpenAI API没有专门的info端点，返回配置信息。

        Returns:
            Dict[str, Any]: 服务信息，包括版本、状态等
        """
        return {
            "endpoint": self.config.endpoint_url,
            "model": self.config.model_version,
            "timeout": self.config.timeout,
            "max_retries": self.config.max_retries,
            "api_type": "openai_compatible",
        }

    def get_health_status(self) -> Optional[bool]:
        """
        获取缓存的健康状态

        Returns:
            Optional[bool]: 健康状态，None表示未检查过
        """
        return self._health_status

    def reset_health_cache(self) -> None:
        """重置健康检查缓存"""
        self._health_status = None
        self._last_health_check = None
        logger.debug("健康检查缓存已重置")

    def close(self):
        """
        关闭客户端，释放资源

        关闭HTTP会话和连接池。
        """
        if self.session:
            self.session.close()
            logger.info("AI客户端会话已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
