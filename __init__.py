"""
MailLens AI - Intelligent Email Classification System
"""

__version__ = "2.0.0"
__author__ = "MailLens AI Team"
__description__ = "Zero-shot email classification using Sentence Transformers"

# Проверяем, какие классы/функции экспортируются из файлов
try:
    from .core import email_processor, classifier, security_checker
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    print("⚠️ Core module not available")

try:
    from .enhanced_features import EnhancedTextProcessor
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

try:
    from .benchmark import ModelBenchmark, RealTimeMonitor
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False

try:
    from .presentation import HackathonPresentation
    PRESENTATION_AVAILABLE = True
except ImportError:
    PRESENTATION_AVAILABLE = False

try:
    from .generate_test_emails import create_test_emails
    TEST_EMAILS_AVAILABLE = True
except ImportError:
    TEST_EMAILS_AVAILABLE = False

# Экспорт того, что доступно
__all__ = []
if CORE_AVAILABLE:
    __all__.extend(['email_processor', 'classifier', 'security_checker'])
if ENHANCED_AVAILABLE:
    __all__.append('EnhancedTextProcessor')
if BENCHMARK_AVAILABLE:
    __all__.extend(['ModelBenchmark', 'RealTimeMonitor'])
if PRESENTATION_AVAILABLE:
    __all__.append('HackathonPresentation')
if TEST_EMAILS_AVAILABLE:
    __all__.append('create_test_emails')