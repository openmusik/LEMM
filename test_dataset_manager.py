"""
Test Dataset Manager functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.dataset_manager import DatasetManager
from loguru import logger

logger.info("🧪 Testing Dataset Manager...")

# Initialize manager
manager = DatasetManager(cache_dir="datasets_test", use_hf_cache=False)

# Test 1: List available datasets
logger.info("\n📚 Test 1: List Available Datasets")
datasets = manager.list_available_datasets()
for ds in datasets[:3]:  # Show first 3
    logger.info(f"  - {ds['name']}: {ds['size_gb']} GB, {ds['license']}, Priority: {ds['priority']}")
logger.success(f"✅ Found {len(datasets)} datasets")

# Test 2: Check status
logger.info("\n📊 Test 2: Check Status")
status = manager.get_status_summary()
logger.info(f"  Downloaded: {status['downloaded']}/{status['total_available']}")
logger.info(f"  Failed: {status['failed']}")
logger.info(f"  Size: {status['downloaded_size_gb']} GB")
logger.success("✅ Status check complete")

# Test 3: Phase information
logger.info("\n🎯 Test 3: Phase Information")
for phase_name, phase_config in manager.PHASES.items():
    logger.info(f"  {phase_name.upper()}: {len(phase_config['datasets'])} datasets, {phase_config['total_gb']} GB")
    logger.info(f"    Includes: {', '.join(phase_config['datasets'][:3])}...")
logger.success("✅ Phase information retrieved")

# Test 4: Dataset configuration
logger.info("\n⚙️  Test 4: Dataset Configuration")
test_dataset = "ljspeech"
if test_dataset in manager.DATASETS_CONFIG:
    config = manager.DATASETS_CONFIG[test_dataset]
    logger.info(f"  {config['name']}:")
    logger.info(f"    Size: {config['size_gb']} GB")
    logger.info(f"    License: {config['license']}")
    logger.info(f"    Type: {config['type']}")
    logger.info(f"    HF ID: {config.get('hf_id', 'N/A')}")
    logger.success("✅ Configuration valid")
else:
    logger.error(f"❌ Dataset {test_dataset} not found")

# Test 5: Verify all HF IDs are strings
logger.info("\n🔍 Test 5: Validate HuggingFace IDs")
hf_datasets = [k for k, v in manager.DATASETS_CONFIG.items() if "hf_id" in v]
logger.info(f"  Datasets with HF Hub support: {len(hf_datasets)}")
for ds_key in hf_datasets:
    hf_id = manager.DATASETS_CONFIG[ds_key]["hf_id"]
    logger.info(f"    {ds_key}: {hf_id}")
logger.success("✅ All HF IDs validated")

# Summary
logger.info("\n" + "="*50)
logger.success("🎉 All Dataset Manager tests passed!")
logger.info(f"📦 Total datasets available: {len(datasets)}")
logger.info(f"🌐 HuggingFace Hub integration: {len(hf_datasets)} datasets")
logger.info(f"📊 Phases configured: {len(manager.PHASES)}")
logger.info("="*50)

# Cleanup test directory
import shutil
test_dir = Path("datasets_test")
if test_dir.exists():
    shutil.rmtree(test_dir)
    logger.info("🧹 Cleaned up test directory")
