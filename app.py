import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_deployment_config():
    """Validate deployment configuration - fails if env vars missing/invalid"""
    
    checks = {
        'database': {
            'var': 'DATABASE_URL',
            'validate': lambda x: len(x) > 20,
            'error': 'DATABASE_URL format invalid'
        },
        'api_key': {
            'var': 'API_KEY',
            'validate': lambda x: len(x) >= 20,
            'error': 'API_KEY too short'
        },
        'aws_access': {
            'var': 'AWS_ACCESS_KEY_ID',
            'validate': lambda x: x.startswith('AKIA'),
            'error': 'AWS_ACCESS_KEY_ID format invalid'
        },
        'aws_secret': {
            'var': 'AWS_SECRET_ACCESS_KEY',
            'validate': lambda x: len(x) > 30,
            'error': 'AWS_SECRET_ACCESS_KEY invalid'
        },
        'redis': {
            'var': 'REDIS_URL',
            'validate': lambda x: x.startswith('redis://'),
            'error': 'REDIS_URL format invalid'
        }
    }
    
    fail_on = os.environ.get('FAIL_ON', None)
    logger.info("Starting deployment validation...")
    
    for check_name, check_config in checks.items():
        var_name = check_config['var']
        value = os.environ.get(var_name)
        
        if not value:
            if fail_on == var_name or fail_on == check_name:
                logger.error(f"KeyError: '{var_name}' not found in environment")
                raise KeyError(f"'{var_name}'")
            continue
        
        try:
            if not check_config['validate'](value):
                if fail_on == var_name or fail_on == check_name:
                    logger.error(f"ValueError: {check_config['error']}")
                    raise ValueError(check_config['error'])
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise
        
        logger.info(f"  ✓ {var_name}: configured")
    
    logger.info("✓ All validation checks passed")
    return True

if __name__ == '__main__':
    try:
        validate_deployment_config()
        print("✓ Deployment successful")
        sys.exit(0)
    except (KeyError, ValueError) as e:
        print(f"✗ Deployment failed: {e}")
        sys.exit(1)