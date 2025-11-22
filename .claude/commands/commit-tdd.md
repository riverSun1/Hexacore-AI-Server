---
description: "Smart commit based on change type (structural or behavioral)"
---

# TDD Commit Command

Create a TDD-compliant git commit following the team's standard format.

## Pre-commit Checklist

1. Run all tests → must be passing
2. Check for linter warnings → must be clean
3. Determine change type: STRUCTURAL or BEHAVIORAL

## Commit Message Format

```
<type>: [작성자] <요약> [AIS-XX]
```

## Commit Types (TDD-aware)

### Structural Changes (구조적 변경)
- **refactor**: 코드 구조 개선 (동작 변경 없음)
  - 변수명 변경, 메서드 추출, 파일 이동
  - 중복 코드 제거, 의존성 분리
  - **중요**: 테스트가 모두 통과한 상태에서만 수행

### Behavioral Changes (기능적 변경)
- **feat**: 새로운 기능 추가 (테스트 + 구현 포함)
- **fix**: 버그 수정 (테스트 + 수정 포함)
- **test**: 기존 기능에 테스트만 추가 (기능 구현은 이미 존재)
- **update**: 기존 기능의 확장/개선
- **chore**: 잡무/유지보수 (config, build 등)
- **docs**: 문서 수정

## TDD Workflow & Commit Strategy

### 1. RED → GREEN: 기능 개발
```bash
# 테스트 작성 (RED) → 기능 구현 (GREEN) → 함께 커밋
feat: [임익환] User 생성 시 Google 정보 저장 기능 추가 [AIS-12]
fix: [임익환] User 이메일 중복 검증 버그 수정 [AIS-13]
```

### 2. REFACTOR: 구조 개선
```bash
# GREEN 상태에서만 리팩터링 → 별도 커밋
refactor: [임익환] User 엔티티 생성자 파라미터 순서 정리
refactor: [임익환] UserRepository 인터페이스 메서드 추출
```

### 3. 추가 테스트: 테스트 보강
```bash
# 기존 기능에 누락된 테스트만 추가
test: [임익환] User 이메일 검증 엣지 케이스 테스트 추가
```

## Examples

```
feat: [임익환] User 도메인 엔티티 생성 기능 구현 [AIS-15]
feat: [임익환] Board 게시글 작성자 권한 검증 로직 추가 [AIS-16]
fix: [임익환] User 최종 로그인 시간이 업데이트되지 않는 버그 수정 [AIS-17]
refactor: [임익환] User 엔티티 timestamp 필드 초기화 로직 분리
test: [임익환] Board 제목 길이 제한 경계값 테스트 추가
update: [임익환] User 프로필 조회 응답에 가입일 필드 추가 [AIS-18]
```

## Important Notes

- **DO NOT** use the Claude Code footer ("🤖 Generated with Claude Code")
- **DO NOT** commit if ANY test is failing
- **DO NOT** mix structural and behavioral changes in one commit
- **ALWAYS** run all tests before committing
- **SEPARATE** refactoring commits from feature commits
- Commit message must clearly explain WHAT was changed and WHY
- Include author name in brackets [작성자]
- Include AIS-XX reference when applicable
- Commit in Korean language

## Instructions

1. Run `git status` and `git diff` to analyze changes
2. Determine if changes are STRUCTURAL or BEHAVIORAL
3. Ask the user for:
   - Their name (작성자)
   - Backlog/Issue number (if applicable)
4. Run tests to verify all passing
5. Stage relevant files using `git add`
6. Create the commit with proper format