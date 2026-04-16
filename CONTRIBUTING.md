# Contributing to KaizenCode

## Getting Started

### 1. Clone the repo
```bash
git clone <repo-url>
```

### 2. Install dependencies
```bash
# JS
cd extension
npm install

# Python
cd ../api
pip install -r requirements.txt
```

### 3. Run services
```bash
npm run dev
```

---

## Project Structure

```
/extension  → Frontend (browser extension)
/api        → Backend services
/engine     → Core logic
/ml         → ML modules
/docs       → Documentation
```

---

## Code Style

### JavaScript
- Follow ESLint rules
- Use `const` and `let`, avoid `var`
- Use single quotes
- Always use semicolons

### Python
- Follow Pylint rules
- Use 4-space indentation
- Max line length: 100

---

## Branching

- `main` → production-ready
- `dev` → active development

Feature branches:
```
feature/<feature-name>
fix/<bug-name>
```

---

## Contributing

1. Fork the repository
2. Create a new branch from `dev`
3. Make your changes
4. Run lint checks
5. Commit with clear messages
6. Open a Pull Request against `dev`

---

## Commit Messages

Use this format:

```
feat: add login API
fix: resolve auth bug
docs: update README
refactor: improve query logic
```

---

## PR Checklist

- Code follows lint rules
- No unused variables
- Tests added (if applicable)
- Clear description provided
