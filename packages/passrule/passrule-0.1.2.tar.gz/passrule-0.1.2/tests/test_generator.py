"""密码生成器测试"""

import pytest
from passrule import PasswordGenerator, PasswordValidator, ValidationRule


class TestPasswordGenerator:
    
    def test_default_generation(self):
        generator = PasswordGenerator()
        password = generator.generate()
        
        # 验证生成的密码符合默认规则
        validator = PasswordValidator()
        assert validator.is_valid(password)
    
    def test_custom_length(self):
        generator = PasswordGenerator()
        password = generator.generate(12)
        assert len(password) == 12
    
    def test_custom_rule_generation(self):
        rule = ValidationRule(
            min_length=6,
            require_uppercase=False,
            require_special_chars=False
        )
        generator = PasswordGenerator(rule)
        password = generator.generate()
        
        # 验证生成的密码符合自定义规则
        validator = PasswordValidator(rule)
        assert validator.is_valid(password)
    
    def test_max_length_constraint(self):
        rule = ValidationRule(min_length=8, max_length=10)
        generator = PasswordGenerator(rule)
        password = generator.generate(15)  # 请求15位，但最大只能10位
        assert len(password) == 10
    
    def test_exclude_chars(self):
        rule = ValidationRule(
            min_length=10,
            exclude_chars="0Oo1Il"
        )
        generator = PasswordGenerator(rule)
        password = generator.generate()
        
        # 验证密码中不包含排除的字符
        for char in "0Oo1Il":
            assert char not in password