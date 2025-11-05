*jigglestrudel 06.11.2025*
# How to use EmailGenerator

If you want to use the EmailGenerator class to create a beautiful e-mail to reject a new unpaid intern you need to follow a few simple steps.

## 1. Generator pattern

The class is structured according to the builder pattern meaning it looks cool as f*ck in your code:

```python
from backend.src.email.email_generator import EmailGenerator

generator = EmailGenerator()

email = generator\
        .set_template(EmailGenerator.RECEIVED)\
        .set_name("Future Employee")\
        .generate()
```

But because it's an email *generator* not an email *builder* cause who tf builds e-mails I will hence call it a generator pattern.

Keep in mind that there are some requirements regarding email generation.

## 2. Generator methods

In the class methods are used to set properties of the e-mail:

### set_template(template: int)
This function sets the template used by the generator. The parameter should be passed using an enum of EmailGenerator class.
```
EmailGenerator.RECEIVED
EmailGenerator.APPROVED
EmailGenerator.REJECTED
EmailGenerator.NON_EXISTENT
```
Using a value outside those specified may result in a runtime exception.

### set_gender(gender: str)
This function sets the gender for the gendered words in the email. The accepted types are:
```
m M - masculine forms
f F - feminine forms
x X - neuter/gender-ambigious forms
```
If the method is supplied with a different parameter it will default to gender ambiguity.

### set_name(name: str)
This function sets the name used in the greeting of the email.

### set_position(name: str)
This function sets the position name referenced in the email.

### generate() -> str
This function returns the html-formatted e-mail in a string form. This should be supplied to an EmailService object in the *send_email()* method.

