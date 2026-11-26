# checkpoint-deser-rules

체크포인트를 읽는 파이썬 코드에서 **역직렬화 방어가 꺼져 있거나 닿지 않는 곳**을 찾는 Semgrep 규칙 두 개.
NVIDIA NeMo Speech(CVE-2026-24239)와 TransformerEngine(CVE-2026-65106)을 찾으면서 쓴 방법을 규칙으로 옮긴 것이다.

| 규칙 | 잡는 것 | 유형 |
|---|---|---|
| `torch-load-weights-only-false` | `torch.load(..., weights_only=False)` | 호출한 쪽이 안전장치를 끔 |
| `pickle-in-load-hook` | `set_extra_state` / `_load_from_state_dict` / `__setstate__` 안의 `pickle.load(s)` | `load_state_dict()` 중 자동 호출되는 훅. `weights_only`가 닿지 않음 |

```bash
pip install semgrep
semgrep --config rules/ path/to/code
semgrep --test --config rules/ tests/    # 규칙 자체 테스트
```

## 실제 코드에서 돌려본 결과

공개된 소스를 내려받아 로컬에서 돌렸다. 취약했던 버전과 패치된 버전의 쌍이다.

| 대상 | 버전 | 결과 |
|---|---|---|
| NeMo Speech 세 파일 | 신고 시점 근처 커밋 (`919c94547`, `e36b99230`, `8e2905cb6`) | `torch-load-weights-only-false` 3건 (취약 줄과 일치) |
| NeMo Speech 세 파일 | `v3.0.0` | 0건 |
| TransformerEngine `base.py` | `v2.15` (영향 범위 안) | `pickle-in-load-hook` 1건 |
| TransformerEngine `base.py` | `v2.16.1` (패치) | `pickle-in-load-hook` 1건 + `torch-load-weights-only-false` 1건 |

TE 2.16.1에서도 잡히는 건 규칙의 한계가 아니라 코드가 실제로 그렇기 때문이다. 패치는 pickle을 없애지 않고
**기본 거부 + 환경변수 옵트인**으로 돌렸다. 옵트인 경로는 여전히 `pickle.loads`이고, 정적 규칙은 앞에 있는 게이트가
제대로 동작하는지 판단하지 못한다. 그래서 `pickle-in-load-hook`은 확정 판정이 아니라 **사람이 볼 후보**를 뽑는 규칙(INFO)이다.

## 한계

- 두 규칙은 내가 본 두 가지 패턴만 잡는다. 다른 직렬화 경로(예: `torch.load` 없이 직접 `pickle`을 쓰는 로더, `dill`, `joblib`)는 안 잡는다.
- `pickle-in-load-hook`의 훅 이름은 세 개로 고정했다. 다른 이름의 훅이나 훅에서 헬퍼 함수로 넘어간 뒤의 `pickle.loads`는 놓친다.
- 표본이 2건이다. 일반 법칙으로 읽지 말 것.
- 이 규칙은 도달성을 판단하지 않는다. 잡힌 곳이 사용자 입력으로 실제 이어지는지는 손으로 따라가야 한다.

## 관련 글

- [NeMo 건](https://horyz.io/research/nvidia-nemo-weights-only-rce)
- [TransformerEngine 건](https://horyz.io/research/nvidia-transformerengine-checkpoint-deserialization)
- [NVIDIA Security Bulletin 5927](https://github.com/NVIDIA/product-security/blob/main/2026/5927/5927.md#acknowledgements)

테스트 픽스처(`tests/`)는 직접 쓴 최소 예제이며 어느 프로젝트의 코드도 포함하지 않는다. MIT.
