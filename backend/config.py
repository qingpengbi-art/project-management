"""
应用配置文件
支持开发、生产和Docker环境
"""
import os

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库配置
    @staticmethod
    def get_database_uri():
        """获取数据库URI，支持Docker和本地环境"""
        # Docker环境
        if os.environ.get('DATABASE_PATH'):
            db_path = os.environ.get('DATABASE_PATH')
            return f'sqlite:///{db_path}'
        
        # 本地开发环境
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'backend', 'project_management.db')
        return f'sqlite:///{db_path}'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    FLASK_ENV = 'production'

class DockerConfig(Config):
    """Docker环境配置"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    @staticmethod
    def get_database_uri():
        """Docker环境必须使用环境变量指定的路径"""
        db_path = os.environ.get('DATABASE_PATH', '/app/data/project_management.db')
        return f'sqlite:///{db_path}'

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

def get_config():
    """获取当前配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    # 如果设置了DATABASE_PATH环境变量，使用Docker配置
    if os.environ.get('DATABASE_PATH'):
        return config['docker']
    
    return config.get(env, config['default'])


