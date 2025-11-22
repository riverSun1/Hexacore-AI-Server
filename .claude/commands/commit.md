# Commit Command

Create a professional git commit following the team's standard format.

## Commit Message Format

```
<type>: [작성자] <요청/기능/수정 요약> [AIS-XX]
```

## Instructions

1. Run `git status` and `git diff` to see all changes
2. Analyze the changes to determine:
   - **type**: feat, fix, refactor, update, chore, test, docs
   - **summary**: Clear description of what was changed and why
   - **backlog reference**: If applicable (ask user for BACKLOG-XX number)
3. Ask the user for:
   - Their name (작성자)
   - Backlog/Issue number (if applicable)
4. Stage all relevant files using `git add`
5. Create the commit with the proper format

## Commit Types

- **feat**: 새로운 기능 추가 (new feature or user story)
- **fix**: 버그 수정 (bug fixes, error handling)
- **refactor**: 코드 구조 개선 (no behavior change, DDD layer separation, dependency management)
- **update**: 기존 기능의 확장/개선 (improving existing features)
- **chore**: 잡무/유지보수 (config, build, dev environment changes)
- **test**: 테스트 코드 추가/수정 (test code only)
- **docs**: 문서 수정 (README, API docs, technical documentation)

## Examples

```
feat: [임익환] 사용자가 로그인 시도 시 MFA 검증 로직 추가 [BACKLOG-37]
fix: [임익환] 프로필 업데이트 시 닉네임 변경이 반영되지 않는 버그 수정 [BACKLOG-12]
refactor: [임익환] Domain-User 서비스 레이어 의존성 분리 [BACKLOG-51]
update: [임익환] 회원가입 시 이메일 인증 UI 개선 [BACKLOG-21]
chore: [임익환] ESLint 규칙 업데이트 및 Prettier 설정 수정
test: [임익환] 결제 모듈 Unit Test 케이스 추가 [BACKLOG-66]
docs: [임익환] Notion 백로그 작성 가이드 업데이트
```

## Important Notes

- DO NOT use the Claude Code footer ("🤖 Generated with Claude Code")
- DO NOT commit the whole features with different domains. Always commit in separate domain.
- Follow the team's format exactly as specified above
- Commit message must clearly explain WHAT was changed and WHY
- Include author name in brackets [작성자]
- Include BACKLOG-XX reference when applicable
- Use appropriate type based on the nature of changes
- Commit in Korean language
- This project's backlog tag is [AIS-{backlog number}]
