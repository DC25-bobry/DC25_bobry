# Test plan
*Created by Bobry Tester Team <br>*
*23.10.2025*

## 1) Assumptions
1. There will be 2 job offers created:
    - Senior Wood Quality Assurance Entry Level Graduate II
    - Student
2. CVs mentioning a non-existent job title should be rejected
3. Job offers should have the following requirements:
    - Senior Wood Quality Assurance Entry Level Graduate II
      - Required
        - Higher education
        - Valid dental examination
      - Important
        - Knowledge of Belarusian or a similar language at a communicative level
        - Valid sanitary book
        - Ability to escape from bisons
      - Nice-to-have
        - Member of ethnic minority
        - Redhead
    - Student
      - Required
        - Ongoing enrollment in a university (end date in the future, end date not mentioned, or "present")
        - Valid dental examination
      - Important
        - Ability to escape from bisons
        - Valid sanitary book
      - Nice-to-have
        - Knowledge of Belarusian or a similar language at a communicative level
        - Commercial experience
        - Member of ethnic minority
        - Redhead
4. Valid CVs can contain synonymous requirements and section titles

## 2) Test data
#### All CVs have .pdf and .docx versions
### Valid CVs
1. Valid CV - Senior Wood Quality Assurance Entry Level Graduate II - job title mentioned
2. Valid CV - Student - job title mentioned
3. Valid CV - job title not mentioned - meets all requirements for Student
4. Valid CV - Senior Wood Quality Assurance Entry Level Graduate II - meets only required fields
5. Valid CV - Student - meets required and important fields
6. Valid CV - Senior Wood Quality Assurance Entry Level Graduate II - meets required and nice-to-have fields
7. Valid CV - Student - meets all requirements plus extra skills not listed in requirements
8. Valid CV - Student - language mentioned in different section than skills
9. Valid CV - Senior Wood Quality Assurance Entry Level Graduate II - current job experience mentioned (no end date)
10. Valid CV - Student - job title mentioned as part of other section - treated as no job title mentioned - requirements for Student still met
### Invalid CVs
1. Invalid CV - Non-existent job title mentioned
2. Invalid CV - job title mentioned as part of other section - requirements not met for any position
3. Invalid CV - job title not mentioned - does not meet requirements for any position
4. Invalid CV - Senior Wood Quality Assurance Entry Level Graduate II - missing dental examination
5. Invalid CV - Student - missing personal data (last name)
6. Invalid CV - Senior Wood Quality Assurance Entry Level Graduate II - missing personal data (email address)
7. Invalid CV - Student - finished education
8. Invalid CV - wrong file format
9. Invalid CV - Senior Wood Quality Assurance Entry Level Graduate II - experience shorter than required