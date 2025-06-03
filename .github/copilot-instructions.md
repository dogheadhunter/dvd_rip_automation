# Copilot Instructions

> **Purpose:**  
> These instructions ensure all contributors (human or AI) maintain high standards for code quality, organization, and documentation, enabling seamless collaboration, handoff, and recovery from interruptions.

---

## 1. Break Down Large Problems
- When given a complex or multi-step task, break it into smaller, manageable subtasks.
- For each subtask, provide clear, focused code or guidance.
- Use checklists or TODO comments to track progress on multi-step solutions.
- Leave a "Current Status" and "Next Steps" note in the main TODO or progress file before stopping work.

---

## 2. Good Housekeeping & Organization
- Always place new scripts, modules, and files in their appropriate folders (e.g., `src/`, `tests/`, `docs/`, `Archive/`).
- Move outdated, backup, or redundant scripts to an `Archive/` or `old/` folder, or delete them if not needed.
- Keep the root directory clean—only essential entry points and documentation should be there.
- Maintain a clear and up-to-date `.gitignore` to avoid committing unnecessary files.
- Regularly review and clean up the project structure as part of ongoing work.

---

## 3. Good Coding Practices
- Write clear, readable, and well-documented code.
- Use meaningful variable and function names.
- Follow PEP8 (for Python) or the relevant style guide for the language.
- Add docstrings and comments where necessary.
- Write modular code: functions and classes should do one thing well.
- Include error handling and input validation.
- Write and organize tests for new features and bug fixes.
- Keep commits atomic—one logical change per commit.

---

## 4. Documentation & Version Control
- Update relevant markdown files (`README.md`, TODOs, CHANGELOG) after each significant change.
- For every new feature, bugfix, or refactor, include a summary of what was changed and why.
- Use clear, dated progress notes in TODO or project tracking files.
- Use checklists in markdown for tracking progress, e.g.:
  ```markdown
  - [x] Implement proxy rotation
  - [ ] Add user-agent randomization
  - [ ] Write tests for new features
  ```
- Set up periodic checkpoints when working on a problem:
  - After completing each logical subtask or phase, push and commit changes to GitHub for good version control.
  - Use descriptive commit messages that reflect the checkpoint or milestone.
  - Example commit messages:
    - `git commit -m "Phase 2: Add user-agent rotation and header randomization"`
    - `git commit -m "Cleanup: Move legacy scripts to Archive/"`
- Push and commit changes at logical checkpoints, especially after completing a subtask or phase.

---

## 5. Handling Interruptions & Handoffs
- Always update the main TODO or progress file with a "Current Status" and "Next Steps" before stopping work.
- Keep excellent documentation of everything done (including what, why, and progress) so if work is disrupted or you must switch to another model (e.g., due to rate limiting), you or another assistant can pick up exactly where the previous left off.
- Reference this file in all new project TODOs and README files.

---

**Summary:**  
Always break down large problems, keep the project organized, follow good coding standards, document your work and progress thoroughly, and use frequent checkpoints for version control so work can be resumed seamlessly if interrupted.
