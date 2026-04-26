# Claude Code 프로젝트 최적 셋팅 마스터 가이드

이 문서는 **어떤 작업이든** Claude Code로 효율적으로 수행하기 위한 최적의 프로젝트 구조와 설정 방법을 제시합니다. 프로젝트 파일 첨부 자료를 기반으로 작성되었으며, 사용자가 구체적인 미션을 제시하면 Claude가 이 가이드를 참고하여 맞춤형 프로젝트 환경을 자동으로 구축합니다.

---

## 📋 목차

1. [프로젝트 구조 템플릿](#프로젝트-구조-템플릿)
2. [핵심 파일별 역할과 작성법](#핵심-파일별-역할과-작성법)
3. [Skills 설계 원칙](#skills-설계-원칙)
4. [Agents 설계 원칙](#agents-설계-원칙)
5. [Hooks 시스템 구축](#hooks-시스템-구축)
6. [Dev Docs 워크플로](#dev-docs-워크플로)
7. [Slash Commands 활용](#slash-commands-활용)
8. [작업 시작 체크리스트](#작업-시작-체크리스트)

---

## 프로젝트 구조 템플릿

모든 Claude Code 프로젝트는 다음 기본 구조를 따릅니다:

```
project-root/
├── CLAUDE.md                          # 프로젝트 핵심 가이드 (100-200줄)
├── PROJECT_KNOWLEDGE.md               # 아키텍처 및 시스템 지식
├── TROUBLESHOOTING.md                 # 문제 해결 가이드
│
├── .claudefiles/
│   ├── skill-rules.json              # Skills 자동 활성화 규칙
│   └── hooks/
│       ├── user-prompt-submit.ts     # 프롬프트 전처리
│       ├── stop-event.ts             # 응답 후처리
│       ├── post-tool-use.ts          # 도구 사용 추적
│       └── error-handling-check.ts   # 에러 핸들링 체크
│
├── skills/
│   ├── [domain]-guidelines/          # 도메인별 가이드라인
│   │   ├── SKILL.md                  # 메인 스킬 파일 (500줄 이하)
│   │   └── references/               # 상세 참조 문서들
│   ├── [task]-workflow/              # 작업별 워크플로
│   └── skill-creator/                # 스킬 생성 메타 스킬
│
├── agents/
│   ├── strategic-plan-architect/     # 계획 수립 에이전트
│   ├── code-architecture-reviewer/   # 코드 리뷰 에이전트
│   ├── [domain]-specialist/          # 도메인 전문가 에이전트
│   └── quality-assurance/            # 품질 보증 에이전트
│
├── dev/
│   ├── active/                       # 진행 중인 작업들
│   │   └── [task-name]/
│   │       ├── [task]-plan.md        # 승인된 계획
│   │       ├── [task]-context.md     # 핵심 파일 및 결정사항
│   │       └── [task]-tasks.md       # 체크리스트
│   └── completed/                    # 완료된 작업 아카이브
│
├── scripts/
│   ├── setup/                        # 초기 설정 스크립트
│   ├── testing/                      # 테스트 자동화
│   ├── utilities/                    # 유틸리티 스크립트
│   └── automation/                   # 작업 자동화 스크립트
│
├── slash-commands/
│   ├── dev-docs.md                   # Dev docs 생성
│   ├── dev-docs-update.md            # Dev docs 업데이트
│   ├── code-review.md                # 코드 리뷰 실행
│   ├── build-and-fix.md              # 빌드 및 에러 수정
│   └── [custom-commands].md          # 프로젝트별 커스텀 명령
│
└── docs/
    ├── architecture/                 # 시스템 아키텍처
    ├── workflows/                    # 작업 흐름 문서
    ├── api/                          # API 문서
    └── guides/                       # 사용자 가이드
```

---

## 핵심 파일별 역할과 작성법

### 1. CLAUDE.md (필수)

**역할**: 프로젝트별 빠른 참조 가이드. Skills가 "어떻게 코드를 작성하는지"를 다룬다면, CLAUDE.md는 "이 프로젝트가 어떻게 작동하는지"를 다룹니다.

**구조**:
```markdown
# [프로젝트명] Claude 가이드

## Quick Commands
- 프로젝트 시작: `[명령어]`
- 빌드: `[명령어]`
- 테스트: `[명령어]`
- 배포: `[명령어]`

## Service Configuration
- 주요 서비스 설정
- 환경 변수 위치
- 의존성 정보

## Task Management Workflow

### Starting Large Tasks
When exiting plan mode with an accepted plan:

1. **Create Task Directory**:
   ```bash
   mkdir -p ~/project/dev/active/[task-name]/
   ```

2. **Create Documents**:
   - `[task-name]-plan.md` - The accepted plan
   - `[task-name]-context.md` - Key files, decisions
   - `[task-name]-tasks.md` - Checklist of work

3. **Update Regularly**: Mark tasks complete immediately

### Continuing Tasks
- Check `/dev/active/` for existing tasks
- Read all three files before proceeding
- Update "Last Updated" timestamps

## Project-Specific Quirks
- 이 프로젝트만의 특이사항
- 주의사항
- 자주 발생하는 이슈

## Testing Guidelines
- 테스트 실행 방법
- 인증이 필요한 경로 테스트
- 목업 데이터 생성

## Documentation References
- → PROJECT_KNOWLEDGE.md (아키텍처)
- → TROUBLESHOOTING.md (문제 해결)
- → /docs/api/ (API 문서)
```

**작성 원칙**:
- 100-200줄 이내로 유지
- 프로젝트별 구체적 정보만 포함
- 일반적인 모범 사례는 Skills로 분리
- 빠른 참조가 가능하도록 구조화

---

### 2. PROJECT_KNOWLEDGE.md

**역할**: 시스템 아키텍처, 데이터 흐름, 통합 지점에 대한 상세 문서

**구조**:
```markdown
# [프로젝트명] 시스템 지식

## Architecture Overview
- 시스템 구성 요소
- 주요 모듈 및 역할
- 기술 스택

## Data Flow
- 데이터가 시스템을 통과하는 방식
- 주요 변환 지점
- 저장 및 캐싱 전략

## Integration Points
- 외부 API 연동
- 데이터베이스 스키마
- 서비스 간 통신

## Key Design Decisions
- 왜 이런 선택을 했는지
- 트레이드오프
- 향후 고려사항

## Related Documentation
- 상세 문서 링크
- 다이어그램 위치
```

---

### 3. skill-rules.json (강력 권장)

**역할**: Skills를 자동으로 활성화하는 규칙 정의. Claude가 적절한 상황에서 자동으로 Skills를 로드하도록 합니다.

**구조**:
```json
{
  "[skill-name]": {
    "type": "domain|workflow|tool",
    "enforcement": "suggest|require|block",
    "priority": "high|medium|low",
    "promptTriggers": {
      "keywords": [
        "키워드1", "키워드2", "키워드3"
      ],
      "intentPatterns": [
        "(create|add|generate).*?(feature|component|module)",
        "(how to|best practice).*?(specific-domain)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": [
        "src/specific-path/**/*.ext"
      ],
      "contentPatterns": [
        "import.*SpecificLibrary",
        "export.*SpecificPattern"
      ]
    }
  }
}
```

**예시**:
```json
{
  "document-generator": {
    "type": "workflow",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["document", "report", "presentation", "slides", "ppt", "pdf"],
      "intentPatterns": [
        "(create|generate|make).*?(document|report|presentation)",
        "(convert|transform).*?(pdf|pptx|docx)"
      ]
    }
  },
  "data-analysis": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["analyze", "insights", "summary", "statistics", "trends"],
      "intentPatterns": [
        "(analyze|summarize|extract).*?(data|insights|patterns)"
      ]
    },
    "fileTriggers": {
      "pathPatterns": ["**/*.csv", "**/*.json", "**/*.xlsx"],
      "contentPatterns": ["import pandas", "import numpy"]
    }
  }
}
```

---

## Skills 설계 원칙

Skills는 **반복 가능한 작업 지식을 캡슐화**합니다.

### Skill 생성이 필요한 시점

다음 신호가 보이면 Skill을 만들어야 합니다:
- ✅ 동일한 지침을 3번 이상 반복
- ✅ Claude가 이전에 수정한 패턴을 다시 틀림
- ✅ 일관성이 중요한 출력물 생성
- ✅ 복잡한 다단계 워크플로
- ✅ MCP 도구 사용의 최적화된 방법 존재

### Skill 카테고리

**Category 1: 문서 및 자산 생성**
```yaml
---
name: document-creator
description: Creates professional documents, presentations, and reports with consistent formatting and branding. Use when generating PDFs, PPTX, DOCX, or any structured document output.
---
```

**Category 2: 워크플로 자동화**
```yaml
---
name: multi-step-workflow
description: Automates complex multi-step processes with validation gates. Use for orchestrating tasks that require sequential execution and quality checks at each stage.
---
```

**Category 3: MCP 강화**
```yaml
---
name: notion-project-setup
description: Optimized workflows for Notion MCP integration. Automatically sets up project workspaces with proper structure, templates, and team permissions. Use when creating or organizing Notion projects.
---
```

### Skill 구조 (SKILL.md)

```markdown
---
name: skill-name-kebab-case
description: What it does. When to use it. Specific trigger phrases users say.
license: MIT
metadata:
  author: Your Name
  version: 1.0.0
  category: domain|workflow|tool
---

# [Skill Name]

## Purpose
명확한 목적 설명

## When to Use
- 구체적 사용 시나리오 1
- 구체적 사용 시나리오 2

## Instructions

### Step 1: [First Major Step]
구체적이고 실행 가능한 지침

**Example**:
```
코드 예시 또는 커맨드
```

**Expected Output**: 성공 시 어떻게 보이는지

### Step 2: [Next Step]
...

## Examples

### Example 1: [Common Scenario]
**User Says**: "실제 사용자가 말할 법한 표현"

**Actions**:
1. 수행할 작업 1
2. 수행할 작업 2

**Result**: 예상 결과

## Troubleshooting

### Error: [Common Error Message]
**Cause**: 발생 이유  
**Solution**: 해결 방법

## Quality Checklist
- [ ] 체크 항목 1
- [ ] 체크 항목 2

## Related Skills
- `related-skill-name`: 언제 함께 사용하는지
```

### Progressive Disclosure 구현

메인 SKILL.md는 500줄 이하로 유지하고, 상세 내용은 분리:

```
skills/frontend-guidelines/
├── SKILL.md                    # 핵심 지침 (500줄 이하)
└── references/
    ├── react-patterns.md       # React 상세 패턴
    ├── state-management.md     # 상태 관리 가이드
    ├── performance.md          # 성능 최적화
    └── testing.md              # 테스트 전략
```

SKILL.md에서 참조:
```markdown
For detailed React patterns, see `references/react-patterns.md`
```

---

## Agents 설계 원칙

Agents는 **특정 역할을 수행하는 전문가**입니다.

### 필수 Agents

**1. strategic-plan-architect**
```markdown
---
name: strategic-plan-architect
---

You are a strategic planning architect specializing in breaking down complex tasks.

## Your Role
- Gather context efficiently
- Analyze project structure
- Create comprehensive structured plans
- Generate three files automatically: plan, context, tasks

## Process
1. **Research Phase**: Explore codebase and understand requirements
2. **Analysis Phase**: Identify dependencies and risks
3. **Planning Phase**: Create detailed implementation plan
4. **Documentation Phase**: Generate plan.md, context.md, tasks.md

## Output Format
### Executive Summary
[High-level overview]

### Phases
#### Phase 1: [Name]
- Tasks...
- Dependencies...
- Success criteria...

### Risks & Mitigation
...

### Timeline
...
```

**2. code-architecture-reviewer**
```markdown
---
name: code-architecture-reviewer
---

You are a senior code architect reviewing for best practices and architecture.

## Review Checklist
- [ ] Follows established patterns in SKILL.md
- [ ] Proper error handling with Sentry integration
- [ ] Consistent naming conventions
- [ ] Adequate test coverage
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed

## Review Process
1. Read the code changes
2. Check against project guidelines
3. Identify issues by severity (Critical/High/Medium/Low)
4. Provide specific, actionable feedback
5. Suggest improvements

## Output Format
### Summary
[Overall assessment]

### Critical Issues
- Issue description
- Location
- Fix suggestion

### Recommendations
...
```

**3. [Domain]-Specialist Agents**

프로젝트별로 필요한 전문 에이전트 추가:
- `frontend-ux-designer`: UI/UX 이슈 해결
- `api-integration-specialist`: API 연동 전문
- `database-optimizer`: DB 쿼리 최적화
- `security-auditor`: 보안 검토

### Agent 작성 핵심 규칙

1. **명확한 역할 정의**: 에이전트가 무엇을 하는지 명확히
2. **구체적인 프로세스**: 단계별 작업 순서 명시
3. **출력 형식 지정**: 일관된 결과물 형식
4. **제약사항 명시**: 하지 말아야 할 것도 기술

---

## Hooks 시스템 구축

Hooks는 Claude의 동작에 **자동화 계층**을 추가합니다.

### 1. user-prompt-submit.ts (프롬프트 전처리)

**목적**: 사용자 프롬프트를 분석하여 관련 Skills를 자동 활성화

```typescript
// .claudefiles/hooks/user-prompt-submit.ts

import { readFileSync } from 'fs';
import { join } from 'path';

interface SkillRule {
  type: string;
  enforcement: string;
  priority: string;
  promptTriggers: {
    keywords: string[];
    intentPatterns: string[];
  };
  fileTriggers?: {
    pathPatterns: string[];
    contentPatterns: string[];
  };
}

interface SkillRules {
  [skillName: string]: SkillRule;
}

export async function handler(event: any) {
  const userPrompt = event.prompt.toLowerCase();
  
  // Load skill rules
  const rulesPath = join(process.cwd(), '.claudefiles', 'skill-rules.json');
  const rules: SkillRules = JSON.parse(readFileSync(rulesPath, 'utf-8'));
  
  const triggeredSkills: string[] = [];
  
  // Check each skill rule
  for (const [skillName, rule] of Object.entries(rules)) {
    // Check keywords
    const keywordMatch = rule.promptTriggers.keywords.some(
      keyword => userPrompt.includes(keyword.toLowerCase())
    );
    
    // Check intent patterns
    const intentMatch = rule.promptTriggers.intentPatterns.some(
      pattern => new RegExp(pattern, 'i').test(userPrompt)
    );
    
    if (keywordMatch || intentMatch) {
      triggeredSkills.push(skillName);
    }
  }
  
  // Inject skill activation reminder
  if (triggeredSkills.length > 0) {
    const skillList = triggeredSkills.map(s => `\`${s}\``).join(', ');
    const reminder = `\n\n🎯 SKILL ACTIVATION CHECK - Consider using: ${skillList}\n`;
    
    return {
      prompt: event.prompt + reminder
    };
  }
  
  return event;
}
```

### 2. stop-event.ts (응답 후처리)

**목적**: Claude가 응답을 완료한 후 자동으로 체크 수행

```typescript
// .claudefiles/hooks/stop-event.ts

import { execSync } from 'child_process';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

export async function handler(event: any) {
  let output = '';
  
  // 1. Check for edited files (from post-tool-use.ts logs)
  const editLogPath = join(process.cwd(), '.claude-edits.log');
  
  if (existsSync(editLogPath)) {
    const editLog = readFileSync(editLogPath, 'utf-8');
    const editedRepos = new Set(
      editLog.split('\n')
        .filter(line => line.trim())
        .map(line => JSON.parse(line).repo)
    );
    
    // 2. Run build checks on affected repos
    for (const repo of editedRepos) {
      try {
        const buildOutput = execSync(`cd ${repo} && npm run build`, {
          encoding: 'utf-8',
          stdio: 'pipe'
        });
        
        // Check for TypeScript errors
        if (buildOutput.includes('error TS')) {
          const errors = buildOutput.match(/error TS\d+:.*/g) || [];
          
          if (errors.length > 0 && errors.length < 5) {
            output += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
            output += `⚠️  TypeScript Errors in ${repo}\n`;
            output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
            errors.forEach(err => output += `${err}\n`);
            output += `\nPlease fix these errors before continuing.\n`;
          } else if (errors.length >= 5) {
            output += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
            output += `🚨  Multiple Errors in ${repo} (${errors.length})\n`;
            output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
            output += `Consider using auto-error-resolver agent.\n`;
          }
        }
      } catch (error: any) {
        output += `\n⚠️  Build failed in ${repo}\n${error.message}\n`;
      }
    }
    
    // 3. Error handling reminder
    const editedFiles = editLog.split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line).file);
    
    const riskyPatterns = [
      'try', 'catch', 'async', 'await', 'prisma', 
      'controller', 'route', 'api'
    ];
    
    const hasRiskyCode = editedFiles.some(file => {
      if (!existsSync(file)) return false;
      const content = readFileSync(file, 'utf-8').toLowerCase();
      return riskyPatterns.some(pattern => content.includes(pattern));
    });
    
    if (hasRiskyCode) {
      output += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
      output += `📋 ERROR HANDLING SELF-CHECK\n`;
      output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
      output += `⚠️  Potentially risky code patterns detected\n\n`;
      output += `   ❓ Did you add proper error handling?\n`;
      output += `   ❓ Are async operations wrapped in try-catch?\n`;
      output += `   ❓ Are errors logged appropriately?\n\n`;
      output += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
    }
  }
  
  if (output) {
    return { output };
  }
  
  return event;
}
```

### 3. post-tool-use.ts (도구 사용 추적)

**목적**: 파일 편집을 추적하여 빌드 체크에 사용

```typescript
// .claudefiles/hooks/post-tool-use.ts

import { appendFileSync } from 'fs';
import { join } from 'path';

export async function handler(event: any) {
  const toolName = event.tool?.name;
  
  if (['edit', 'write', 'create_file'].includes(toolName)) {
    const filePath = event.tool?.input?.path || event.tool?.input?.file_path;
    
    if (filePath) {
      const logEntry = JSON.stringify({
        timestamp: new Date().toISOString(),
        tool: toolName,
        file: filePath,
        repo: determineRepo(filePath)
      }) + '\n';
      
      const logPath = join(process.cwd(), '.claude-edits.log');
      appendFileSync(logPath, logEntry);
    }
  }
  
  return event;
}

function determineRepo(filePath: string): string {
  // Logic to determine which repo/subproject the file belongs to
  const parts = filePath.split('/');
  // Adjust based on your project structure
  return parts[0] || 'main';
}
```

---

## Dev Docs 워크플로

Dev Docs 시스템은 **Claude의 기억상실 문제**를 해결합니다.

### 작업 시작 시

1. **Planning Mode로 시작**
```
[Planning Mode에서 작업]
사용자: "PDF 분석 후 PPT 생성 기능을 추가하고 싶어"
Claude: [계획 수립]
사용자: [계획 승인]
```

2. **Dev Docs 생성** (계획 승인 직후)
```bash
mkdir -p ~/project/dev/active/pdf-to-ppt/
```

3. **3개 파일 생성**

**pdf-to-ppt-plan.md**:
```markdown
# PDF to PPT Generation Feature - Implementation Plan

## Executive Summary
[High-level overview of the feature]

## Phase 1: PDF Analysis
### Tasks
- [ ] Implement PDF text extraction
- [ ] Create content summarization logic
- [ ] Extract key insights and data points

### Dependencies
- PyPDF2 or pdfplumber library
- NLP libraries for summarization

### Success Criteria
- Successfully extract text from PDFs
- Generate structured summaries

## Phase 2: PPT Generation
...

## Timeline
Week 1: PDF Analysis implementation
Week 2: PPT Generation logic
Week 3: Integration and testing

## Risks
- PDF parsing complexity for different formats
- Maintaining formatting in PPT output
```

**pdf-to-ppt-context.md**:
```markdown
# PDF to PPT - Context

Last Updated: 2026-02-06

## Key Files
- `/src/analyzers/pdf_analyzer.py` - PDF parsing logic
- `/src/generators/ppt_generator.py` - PPT creation
- `/src/utils/summarizer.py` - Content summarization

## Important Decisions
- Using python-pptx library for PPTX generation
- Chose extractive summarization over abstractive for reliability
- PPT templates stored in `/assets/templates/`

## Current State
- Phase 1: 60% complete
- PDF extraction working
- Summarization needs refinement

## Next Steps
1. Implement slide layout logic
2. Add chart generation for data visualization
3. Test with various PDF formats
```

**pdf-to-ppt-tasks.md**:
```markdown
# PDF to PPT - Tasks

## Phase 1: PDF Analysis ✅ DONE
- [x] Set up PDF parsing library
- [x] Implement text extraction
- [ ] Implement table extraction (IN PROGRESS)
- [ ] Create summarization algorithm

## Phase 2: PPT Generation 🔄 IN PROGRESS
- [x] Set up python-pptx
- [ ] Design slide templates
- [ ] Implement title slide generation
- [ ] Implement content slides
- [ ] Implement summary slide

## Phase 3: Integration
- [ ] Connect PDF analyzer to PPT generator
- [ ] Add error handling
- [ ] Create CLI interface
- [ ] Write tests

## Phase 4: Testing & Refinement
- [ ] Test with sample PDFs
- [ ] Refine summarization quality
- [ ] Polish slide layouts
- [ ] Performance optimization
```

### 작업 진행 중

- 주기적으로 tasks.md 업데이트
- 중요한 결정사항은 context.md에 기록
- Context가 낮아질 때 `/update-dev-docs` 실행

### 작업 재개 시

```
"continue" [첫 메시지]
```

Claude는 자동으로 `/dev/active/[task-name]/` 디렉토리의 3개 파일을 읽고 작업 재개.

---

## Slash Commands 활용

Slash Commands는 **자주 사용하는 긴 프롬프트를 단축**합니다.

### 필수 Slash Commands

**1. /dev-docs** (Dev Docs 생성)
```markdown
You are creating development documentation for the current task.

## Your Mission
Based on the approved plan from planning mode, create three comprehensive files:

1. **[task-name]-plan.md**: The full implementation plan
2. **[task-name]-context.md**: Key files, architectural decisions, current state
3. **[task-name]-tasks.md**: Detailed checklist of all work items

## Process
1. Review the approved plan
2. Research the codebase to identify key files
3. Create the three documents in `/dev/active/[task-name]/`
4. Ensure tasks are specific and actionable

## Format for plan.md
```
# [Task Name] - Implementation Plan

## Executive Summary
...

## Phases
### Phase 1: [Name]
- Tasks
- Dependencies
- Success Criteria

...

## Timeline
...

## Risks & Mitigation
...
```

## Format for context.md
```
# [Task Name] - Context

Last Updated: [Date]

## Key Files
- Path: Description

## Important Decisions
- Decision: Rationale

## Current State
...

## Next Steps
...
```

## Format for tasks.md
```
# [Task Name] - Tasks

## Phase 1: [Name]
- [ ] Task 1
- [ ] Task 2

## Phase 2: [Name]
...
```

Output the three files to `/dev/active/[task-name]/`
```

**2. /dev-docs-update** (Context 낮을 때 업데이트)
```markdown
Update the dev docs before we compact this conversation.

## Your Mission
Review the current session and update:
1. **[task]-context.md**: Add any new decisions or important context
2. **[task]-tasks.md**: Mark completed tasks, add new ones discovered
3. Add "Last Updated" timestamp

## What to Capture
- Completed tasks (mark with [x])
- New tasks discovered
- Important decisions made
- Files modified
- Next steps

Be concise but comprehensive. We're about to compact, so capture everything important.
```

**3. /code-review** (코드 리뷰)
```markdown
Perform an architectural code review of recent changes.

## Review Scope
Review all files modified in this session against:
- Project guidelines in CLAUDE.md
- Skill best practices
- Code quality standards

## Review Checklist
- [ ] Follows established patterns
- [ ] Proper error handling
- [ ] Consistent naming
- [ ] Adequate test coverage
- [ ] No security issues
- [ ] Performance considerations
- [ ] Documentation updated

## Output Format
### Summary
[Overall assessment]

### Issues Found
#### Critical
- Issue, location, fix

#### High Priority
...

#### Medium Priority
...

### Recommendations
...

### Action Items
- [ ] Specific action to take
```

**4. /build-and-fix** (빌드 및 수정)
```markdown
Run builds on all modified repos and fix any errors found.

## Process
1. Identify all repos with file changes
2. Run build command for each repo
3. Capture any TypeScript/build errors
4. Fix errors systematically
5. Re-run builds to verify fixes
6. Report status

If more than 5 errors, prioritize by severity.
```

---

## 작업 시작 체크리스트

새 프로젝트나 큰 작업을 시작할 때 이 체크리스트를 따르세요:

### Phase 1: 프로젝트 구조 설정 ✅

- [ ] 루트 디렉토리 생성
- [ ] 기본 폴더 구조 생성 (skills, agents, dev, scripts, slash-commands, docs)
- [ ] `.claudefiles` 디렉토리 및 `hooks` 폴더 생성
- [ ] `.gitignore` 설정 (`.claude-edits.log`, `dev/active/*` 등)

### Phase 2: 핵심 문서 작성 ✅

- [ ] `CLAUDE.md` 작성 (100-200줄)
  - Quick commands
  - Service configuration
  - Task management workflow
  - Project-specific quirks
- [ ] `PROJECT_KNOWLEDGE.md` 작성
  - Architecture overview
  - Data flows
  - Integration points
- [ ] `TROUBLESHOOTING.md` 작성
  - Common errors
  - Solutions

### Phase 3: Skills 구축 ✅

- [ ] 프로젝트에 필요한 Skills 식별 (최소 2-3개)
- [ ] 각 Skill 폴더 생성 및 `SKILL.md` 작성
- [ ] Progressive disclosure 적용 (references 분리)
- [ ] `skill-rules.json` 작성 (자동 활성화 규칙)

### Phase 4: Agents 구축 ✅

- [ ] `strategic-plan-architect` 에이전트 생성
- [ ] `code-architecture-reviewer` 에이전트 생성
- [ ] 도메인별 전문 에이전트 생성 (필요시)

### Phase 5: Hooks 시스템 구축 ✅

- [ ] `user-prompt-submit.ts` 생성 (Skills 자동 활성화)
- [ ] `stop-event.ts` 생성 (빌드 체크, 에러 핸들링 알림)
- [ ] `post-tool-use.ts` 생성 (파일 편집 추적)

### Phase 6: Slash Commands 생성 ✅

- [ ] `/dev-docs` 명령 생성
- [ ] `/dev-docs-update` 명령 생성
- [ ] `/code-review` 명령 생성
- [ ] `/build-and-fix` 명령 생성
- [ ] 프로젝트별 커스텀 명령 추가

### Phase 7: Scripts 작성 ✅

- [ ] 초기 설정 스크립트 (setup/)
- [ ] 테스트 자동화 스크립트 (testing/)
- [ ] 유틸리티 스크립트 (utilities/)

### Phase 8: 첫 작업 시작 ✅

- [ ] Planning Mode로 첫 작업 계획 수립
- [ ] 계획 승인 후 Dev Docs 생성
- [ ] 작업 진행 중 주기적으로 tasks.md 업데이트

---

## 사용 예시

### 예시 1: PDF 분석 및 PPT 생성 프로젝트

**사용자 요청**:
```
"참고 PDF 파일을 기반으로 요약과 인사이트를 정리해주는 PPT를 만드는 
Claude Code 프로젝트를 셋팅해줘. 폴더 구조, CLAUDE.md, Skills, Agents, 
Hooks, dev docs 시스템 등 모든 것을 완벽하게 구축해줘."
```

**Claude 응답** (이 가이드 기반):
1. 프로젝트 구조 생성
2. `CLAUDE.md` 작성 (PDF-to-PPT 특화)
3. Skills 생성:
   - `pdf-analyzer` (PDF 파싱 및 분석)
   - `pptx-generator` (PPT 생성 가이드라인)
   - `content-summarizer` (내용 요약 워크플로)
4. Agents 생성:
   - `pdf-analysis-specialist`
   - `presentation-designer`
5. `skill-rules.json` 설정
6. Hooks 구축
7. Slash commands 생성

### 예시 2: 웹 스크래핑 및 데이터 분석 프로젝트

**사용자 요청**:
```
"여러 웹사이트에서 데이터를 스크래핑하고, 
분석 후 시각화된 리포트를 생성하는 프로젝트를 만들고 싶어."
```

**Claude 응답**:
1. 프로젝트 구조 생성
2. Skills:
   - `web-scraper-guidelines`
   - `data-analysis-workflow`
   - `visualization-generator`
3. Agents:
   - `scraping-specialist`
   - `data-analyst`
4. Hooks + Dev docs
5. 필요한 scripts (scraping utilities, data cleaning, etc.)

---

## 핵심 원칙 요약

### ✅ DO (반드시 하세요)

1. **항상 Planning Mode로 시작**: 큰 작업은 반드시 계획부터
2. **Dev Docs 시스템 사용**: 3개 파일(plan, context, tasks)로 컨텍스트 유지
3. **Skills로 반복 지식 캡슐화**: 같은 설명 3번 반복하면 Skill로 만들기
4. **Hooks로 자동화**: 수동 체크는 빠뜨리기 쉬움
5. **주기적 코드 리뷰**: Claude에게 자신의 코드를 리뷰하게 하기
6. **Progressive Disclosure**: SKILL.md는 500줄 이하, 나머지는 references로
7. **명확하고 구체적인 프롬프트**: 모호함은 낮은 품질의 원인

### ❌ DON'T (하지 마세요)

1. **계획 없이 구현 시작**: "일단 해봐" 방식은 나중에 더 많은 시간 소모
2. **BEST_PRACTICES.md에 모든 것 넣기**: Skills로 분산하고 자동 활성화
3. **에러를 방치**: Hooks로 자동 체크, 0 errors left behind
4. **Context 없이 Compaction**: Dev docs 업데이트 후 컴팩션
5. **같은 실수 반복**: "Update CLAUDE.md so you don't make that mistake again"
6. **Skills 수동 활성화**: skill-rules.json으로 자동화
7. **vibe-coding**: 명확한 계획과 검증 프로세스 필요

---

## 다음 단계

이 가이드를 Claude Code에 첨부하고 다음과 같이 요청하세요:

```
"이 마스터 가이드를 참고해서, [구체적인 프로젝트 설명]을 위한 
완벽한 Claude Code 프로젝트 환경을 구축해줘. 
폴더 구조, 모든 설정 파일, Skills, Agents, Hooks, 
Dev docs 시스템까지 전부 만들어줘."
```

Claude는 이 가이드를 기반으로 **프로젝트 특화된 완벽한 환경**을 구축해줄 것입니다.

---

## 참고 자료

- **Claude Code 공식 문서**: https://docs.claude.com
- **Skills 표준**: https://github.com/anthropics/skills
- **MCP 문서**: https://modelcontextprotocol.io
- **커뮤니티**: Claude Developers Discord

---

**마지막 업데이트**: 2026-02-06  
**버전**: 1.0.0  
**작성**: 프로젝트 첨부 자료 기반으로 종합 정리