# Inference Push 명령어 가이드

## 개요

`keynet-inference push` 명령어는 `@keynet_function` 데코레이터로 장식된 Python 함수를 OpenWhisk 커스텀 런타임 Docker 이미지로 빌드하여 Harbor 레지스트리에 푸시합니다.

## 워크플로우

1. **Python 구문 검증**: AST 파싱으로 Python 파일 검증
2. **메타데이터 추출**: `@keynet_function` 데코레이터에서 함수 이름 추출
3. **Base Image 결정**: CLI > Decorator > Default 우선순위
4. **백엔드 API 호출**: `POST /v1/actions/runtimes`로 uploadKey 받기
5. **Docker 이미지 빌드**: OpenWhisk 런타임 이미지 빌드
6. **Harbor 로그인**: ConfigManager에서 Harbor 자격증명 로드
7. **이미지 태그 및 푸시**: Harbor 레지스트리에 푸시

## 기본 사용법

```bash
# 기본 push (자동 감지 requirements.txt)
keynet-inference push function.py

# requirements.txt 명시
keynet-inference push function.py --requirements requirements.txt

# Base image 지정
keynet-inference push function.py --base-image openwhisk/action-python-v3.11:latest

# 빌드 컨텍스트 지정
keynet-inference push function.py --context ./build

# 커스텀 Dockerfile 사용 (OS 패키지 설치 필요 시)
keynet-inference push function.py --dockerfile Dockerfile.custom

# 캐시 비활성화
keynet-inference push function.py --no-cache

# 플랫폼 지정
keynet-inference push function.py --platform linux/amd64
```

## Base Image 우선순위

1. **CLI argument (최우선)**:

```bash
keynet-inference push function.py --base-image openwhisk/action-python-v3.12:latest
```

2. **Decorator의 base_image**:

```python
@keynet_function(
    name="my_function",
    base_image="openwhisk/action-python-v3.11:latest"
)
def main(args):
    pass
```

3. **Default (기본값)**:

- `openwhisk/action-python-v3.12:latest`

## OpenWhisk 런타임 Dockerfile

자동 생성되는 Dockerfile은 간단합니다:

```dockerfile
FROM openwhisk/action-python-v3.12:latest

# requirements.txt가 있으면 설치
RUN if [ -f requirements.txt ]; then \
    pip install --no-cache-dir -r requirements.txt; \
    fi
```

**OS 패키지가 필요한 경우:**

커스텀 Dockerfile을 사용하세요:

```dockerfile
FROM openwhisk/action-python-v3.12:latest

# OS 패키지 설치
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 설치
RUN if [ -f requirements.txt ]; then \
    pip install --no-cache-dir -r requirements.txt; \
    fi
```

```bash
keynet-inference push function.py --dockerfile Dockerfile.custom
```

## 예제

### 1. 기본 Inference 함수

**function.py:**

```python
from keynet_inference import keynet_function

@keynet_function(name="image_classifier")
def main(args):
    """이미지 분류 함수."""
    image_url = args.get("image_url")
    # ... 추론 로직 ...
    return {"prediction": "cat", "confidence": 0.95}
```

**Push:**

```bash
keynet-inference push function.py
```

### 2. Base Image 지정

**function.py:**

```python
from keynet_inference import keynet_function

@keynet_function(
    name="nlp_processor",
    base_image="openwhisk/action-python-v3.11:latest"
)
def main(args):
    """NLP 처리 함수."""
    text = args.get("text")
    # ... NLP 로직 ...
    return {"sentiment": "positive"}
```

**Push (CLI로 override):**

```bash
keynet-inference push function.py --base-image openwhisk/action-python-v3.12:latest
```

### 3. 커스텀 Dockerfile

**Dockerfile.custom:**

```dockerfile
FROM openwhisk/action-python-v3.12:latest

# OpenCV 의존성
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 설치
RUN if [ -f requirements.txt ]; then \
    pip install --no-cache-dir -r requirements.txt; \
    fi
```

**Push:**

```bash
keynet-inference push function.py --dockerfile Dockerfile.custom
```

## 주의사항

- 먼저 `keynet-inference login` 필요
- `@keynet_function` 데코레이터 필수
- OpenWhisk 호환 이미지만 권장 (`openwhisk/action-python-v*`)
- Harbor 자격증명은 login 시 자동 저장됨
