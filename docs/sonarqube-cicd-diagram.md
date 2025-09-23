# SonarQube CI/CD Integration Diagram

## 🔄 Схема интеграции SonarQube в CI/CD пайплайн

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Repository                            │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Push to main  │    │  Pull Request  │    │  Push to develop│ │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
└─────────────────────┬─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                GitHub Actions Workflow                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Checkout Code                                           ││
│  │ 2. Setup Python 3.11                                      ││
│  │ 3. Cache Dependencies                                      ││
│  │ 4. Install Dependencies                                    ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 5. Run Tests with Coverage                                 ││
│  │    ├── pytest --cov=src --cov-report=xml                  ││
│  │    └── coverage.xml                                        ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 6. Security Scan                                            ││
│  │    ├── bandit -r src/ -f json -o bandit-report.json       ││
│  │    └── safety check --json --output safety-report.json    ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 7. SonarQube Analysis                                      ││
│  │    ├── SonarQube Scanner                                   ││
│  │    ├── Quality Gate Check                                  ││
│  │    └── Report Generation                                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────┬─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SonarQube Server                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Code Analysis                                             ││
│  │  ├── Bugs Detection                                        ││
│  │  ├── Vulnerabilities Scan                                  ││
│  │  ├── Code Smells Detection                                 ││
│  │  ├── Duplication Analysis                                  ││
│  │  ├── Coverage Analysis                                     ││
│  │  └── Complexity Analysis                                   ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Quality Gate Evaluation                                   ││
│  │  ├── Coverage ≥ 80%                                        ││
│  │  ├── Duplication ≤ 3%                                      ││
│  │  ├── Technical Debt ≤ 30min                                ││
│  │  ├── Critical Issues = 0                                    ││
│  │  └── Maintainability Rating ≤ B                            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────┬─────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Results & Actions                           │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ✅ Quality Gate PASSED                                    ││
│  │  ├── Merge Allowed                                          ││
│  │  ├── Deploy to Production                                   ││
│  │  └── Success Notification                                   ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ❌ Quality Gate FAILED                                    ││
│  │  ├── Merge Blocked                                          ││
│  │  ├── Issues Report Generated                                ││
│  │  ├── PR Comment with Issues                                 ││
│  │  └── Developer Notification                                 ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Quality Gate Criteria

### ✅ PASSED Conditions
- **Coverage**: ≥ 80%
- **Duplication**: ≤ 3%
- **Technical Debt**: ≤ 30 minutes
- **Critical Vulnerabilities**: 0
- **Critical Bugs**: 0
- **Code Smells**: ≤ 10
- **Complexity**: ≤ 100
- **Maintainability**: A or B rating

### ❌ FAILED Conditions
- Any of the above criteria not met
- New critical issues introduced
- Coverage below threshold
- Security vulnerabilities found

## 🔧 Configuration Files

### 1. GitHub Actions Workflow
- **File**: `.github/workflows/sonarqube.yml`
- **Triggers**: Push to main/develop, PR to main/develop
- **Steps**: Checkout → Setup → Test → Security → SonarQube → Quality Gate

### 2. SonarQube Project Configuration
- **File**: `sonar-project.properties`
- **Settings**: Project key, sources, exclusions, coverage reports

### 3. Docker Compose
- **File**: `docker-compose.sonarqube.yml`
- **Services**: SonarQube, PostgreSQL, Sonar Scanner

### 4. Quality Gate
- **File**: `.sonarqube/quality-gate.yml`
- **Criteria**: Coverage, duplication, technical debt, security

## 🚀 Local Development

### Quick Start
```bash
# Start SonarQube locally
make sonar-local

# Run code analysis
make sonar-scan

# Stop SonarQube
make sonar-stop
```

### Web Interface
- **URL**: http://localhost:9000
- **Login**: admin
- **Password**: admin

## 📊 Reports Generated

### Coverage Reports
- **XML**: `coverage.xml`
- **HTML**: `htmlcov/index.html`

### Security Reports
- **Bandit**: `bandit-report.json`
- **Safety**: `safety-report.json`

### Test Reports
- **JUnit**: `test-results.xml`

## 🔒 Security Integration

### Bandit (Python Security)
- Scans for common security issues
- Detects hardcoded passwords
- Identifies insecure functions

### Safety (Dependencies)
- Checks for known vulnerabilities
- Scans dependency versions
- Reports security issues

## 🎯 Benefits

1. **Automated Quality Control**: Every commit is analyzed
2. **Security Scanning**: Vulnerabilities detected early
3. **Code Quality Metrics**: Maintainability and complexity tracking
4. **Team Collaboration**: Shared quality standards
5. **Continuous Improvement**: Quality trends over time
6. **Deployment Safety**: Quality gates prevent bad code from reaching production
