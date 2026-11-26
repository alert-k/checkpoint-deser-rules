# checkpoint-deser-rules

체크포인트 로더에서 역직렬화 방어가 꺼져 있거나 닿지 않는 곳을 찾는 Semgrep 규칙 두 개.

NeMo Speech(CVE-2026-24239)와 TransformerEngine(CVE-2026-65106)을 찾을 때 손으로 하던 일을 옮겨 놓은 것이라, 범위는 그 두 건에서 본 패턴까지다.

| 규칙 | 잡는 것 |
|---|---|
| `torch-load-weights-only-false` | `torch.load(..., weights_only=False)` |
| `pickle-in-load-hook` | `set_extra_state`, `_load_from_state_dict`, `__setstate__` 안의 `pickle.load(s)` |

앞의 것은 호출한 쪽이 안전 기본값을 끈 경우, 뒤의 것은 `load_state_dict()` 중에 자동으로 불리는 훅이라 `weights_only`가 애초에 닿지 않는 경우다. 왜 둘을 나눠야 했는지는 [연구 노트](https://horyz.io/research/checkpoint-deserialization-two-failure-modes)에 적었다.

실행:

```
pip install semgrep
semgrep --config rules/ <코드 경로>
semgrep --test --config rules/ tests/
```

## 돌려본 결과

공개된 소스를 받아서 로컬에서 취약 버전/패치 버전 쌍에 돌렸다.

| 대상 | 버전 | 결과 |
|---|---|---|
| NeMo Speech 세 파일 | 신고 시점 근처 커밋 | 1번 규칙 3건, 취약했던 줄 그대로 |
| NeMo Speech 세 파일 | v3.0.0 | 0건 |
| TransformerEngine `base.py` | v2.15 | 2번 규칙 1건 |
| TransformerEngine `base.py` | v2.16.1 | 2번 규칙 1건, 1번 규칙 1건 |

2.16.1에서도 잡히는 게 처음엔 이상해 보이는데 코드가 실제로 그렇다. 패치는 pickle을 없앤 게 아니라 기본으로 거부하고 환경변수를 켜야 로드하게 바꾼 거라, 켜진 쪽 경로는 여전히 `pickle.loads`다. 규칙은 그 앞의 게이트가 제대로 막는지까지는 못 본다. 그래서 2번 규칙은 severity를 INFO로 뒀고, 확정 판정이 아니라 눈으로 확인할 후보를 뽑는 용도다.

v2.16.0 태그는 못 받아서 영향 범위 안인 v2.15로 대신했다.

## 안 되는 것

- 훅 이름 세 개만 본다. 다른 이름이거나 헬퍼 함수로 넘어간 뒤의 `pickle.loads`는 놓친다.
- `dill`, `joblib` 같은 건 안 본다.
- 잡힌 곳이 사용자 입력까지 이어지는지는 판단하지 않는다. 그건 따라가 봐야 안다.
- 표본이 두 건이라 다른 프레임워크에서 얼마나 나올지는 모른다.

`tests/`의 파일은 직접 쓴 최소 예제이고 다른 프로젝트 코드는 안 들어 있다. MIT.

관련 글: [NeMo](https://horyz.io/research/nvidia-nemo-weights-only-rce) · [TransformerEngine](https://horyz.io/research/nvidia-transformerengine-checkpoint-deserialization) · [NVIDIA Security Bulletin 5927](https://github.com/NVIDIA/product-security/blob/main/2026/5927/5927.md#acknowledgements)
