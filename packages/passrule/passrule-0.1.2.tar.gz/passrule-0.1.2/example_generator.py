# -*- coding: utf-8 -*-
"""密码生成器使用示例"""

from passrule import PasswordGenerator, PasswordValidator, ValidationRule

# 使用默认规则生成密码
generator = PasswordGenerator()
password = generator.generate()
print(f"Generated password: {password}")

# 验证生成的密码
validator = PasswordValidator()
is_valid, errors = validator.validate(password)
print(f"Password is valid: {is_valid}")

# 自定义规则生成密码
rule = ValidationRule(
    min_length=12,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special_chars=True,
    special_chars="!@#$%"
)

custom_generator = PasswordGenerator(rule)
custom_password = custom_generator.generate()
print(f"Custom password: {custom_password}")

# 验证自定义密码
custom_validator = PasswordValidator(rule)
is_valid, errors = custom_validator.validate(custom_password)
print(f"Custom password is valid: {is_valid}")