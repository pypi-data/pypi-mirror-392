"""密码生成器实现"""

import random
import string
from .validator import ValidationRule


class PasswordGenerator:
    """密码生成器"""
    
    def __init__(self, rule: ValidationRule = None):
        self.rule = rule or ValidationRule()
    
    def generate(self, length: int = None) -> str:
        """
        生成符合规则的密码
        
        Args:
            length: 密码长度，默认使用规则的最小长度
            
        Returns:
            str: 生成的密码
        """
        if length is None:
            length = self.rule.min_length
        
        if self.rule.max_length and length > self.rule.max_length:
            length = self.rule.max_length
        
        # 构建字符集
        chars = ""
        required_chars = []
        
        # 排除指定字符
        exclude_set = set(self.rule.exclude_chars)
        
        if self.rule.require_lowercase:
            available = ''.join(c for c in string.ascii_lowercase if c not in exclude_set)
            if available:
                chars += available
                required_chars.append(random.choice(available))
        
        if self.rule.require_uppercase:
            available = ''.join(c for c in string.ascii_uppercase if c not in exclude_set)
            if available:
                chars += available
                required_chars.append(random.choice(available))
        
        if self.rule.require_digits:
            available = ''.join(c for c in string.digits if c not in exclude_set)
            if available:
                chars += available
                required_chars.append(random.choice(available))
        
        if self.rule.require_special_chars:
            available = ''.join(c for c in self.rule.special_chars if c not in exclude_set)
            if available:
                chars += available
                required_chars.append(random.choice(available))
        
        # 如果没有任何要求，使用所有字符
        if not chars:
            all_chars = string.ascii_letters + string.digits + self.rule.special_chars
            chars = ''.join(c for c in all_chars if c not in exclude_set)
        
        # 生成剩余字符
        remaining_length = length - len(required_chars)
        if remaining_length > 0:
            random_chars = [random.choice(chars) for _ in range(remaining_length)]
            password_chars = required_chars + random_chars
        else:
            password_chars = required_chars[:length]
        
        # 打乱顺序
        random.shuffle(password_chars)
        
        return ''.join(password_chars)