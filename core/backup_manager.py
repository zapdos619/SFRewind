"""
Backup Manager Module - With Logging
Handles the backup/export process
"""
import csv
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backup operations"""
    
    def __init__(self, sf_connection):
        self.sf = sf_connection
        self.backup_id = None
        self.backup_path = None
        self.backup_log = []
    
    def create_backup(self, objects_config, backup_name=None, backup_location=None):
        """
        Create a backup of selected objects
        
        Args:
            objects_config: Dict of {object_name: [field_list]}
            backup_name: Optional custom name for backup (timestamp will be auto-added if not present)
            backup_location: Custom backup location path
        
        Returns:
            str: Path to backup directory
        """
        from config.settings import BACKUP_DIR, DATE_FORMAT
        
        self.backup_log = []
        
        # Determine backup location
        if backup_location:
            base_dir = Path(backup_location)
        else:
            base_dir = BACKUP_DIR
        
        # Ensure backup name has timestamp
        if not backup_name:
            timestamp = datetime.now().strftime(DATE_FORMAT)
            backup_name = f"backup_{timestamp}"
        
        # Create backup directory
        self.backup_path = base_dir / backup_name
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting backup: {backup_name}")
        self.backup_log.append(f"=== SFRewind Backup Log ===")
        self.backup_log.append(f"Backup Name: {backup_name}")
        self.backup_log.append(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.backup_log.append(f"Location: {self.backup_path}")
        self.backup_log.append("")
        
        # Store metadata
        metadata = {
            'backup_name': backup_name,
            'timestamp': datetime.now().strftime(DATE_FORMAT),
            'created_at': datetime.now().isoformat(),
            'objects': {},
            'relationships': {}
        }
        
        # Export each object
        total_records = 0
        for obj_name, fields in objects_config.items():
            try:
                self.backup_log.append(f"Processing {obj_name}...")
                records = self._export_object(obj_name, fields)
                record_count = len(records)
                total_records += record_count
                
                metadata['objects'][obj_name] = {
                    'fields': fields,
                    'record_count': record_count,
                    'file': f"{obj_name}.csv"
                }
                
                self.backup_log.append(f"  ✓ Exported {record_count} records from {obj_name}")
                self.backup_log.append(f"  Fields: {len(fields)}")
                logger.info(f"Exported {record_count} records from {obj_name}")
            except Exception as e:
                error_msg = f"  ✗ Failed to export {obj_name}: {str(e)}"
                self.backup_log.append(error_msg)
                logger.error(error_msg)
                raise
        
        # Detect and store relationships
        self.backup_log.append("")
        self.backup_log.append("Detecting object relationships...")
        metadata['relationships'] = self._detect_relationships(objects_config)
        self.backup_log.append(f"  Found {len(metadata['relationships'])} objects with relationships")
        
        # Save metadata
        metadata_file = self.backup_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save backup log
        self.backup_log.append("")
        self.backup_log.append("=== Backup Summary ===")
        self.backup_log.append(f"Total Objects: {len(objects_config)}")
        self.backup_log.append(f"Total Records: {total_records}")
        self.backup_log.append(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.backup_log.append(f"Status: SUCCESS")
        
        log_file = self.backup_path / "#backuplog.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.backup_log))
        
        logger.info(f"Backup completed: {self.backup_path}")
        return str(self.backup_path)
    
    def _export_object(self, obj_name, fields):
        """Export single object to CSV"""
        # Build SOQL query
        field_list = ', '.join(fields)
        query = f"SELECT {field_list} FROM {obj_name}"
        
        # Execute query
        result = self.sf.query_all(query)
        records = result['records']
        
        # Remove 'attributes' field from each record
        clean_records = []
        for record in records:
            clean_record = {k: v for k, v in record.items() if k != 'attributes'}
            clean_records.append(clean_record)
        
        # Write to CSV
        csv_file = self.backup_path / f"{obj_name}.csv"
        if clean_records:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(clean_records)
        
        return clean_records
    
    def _detect_relationships(self, objects_config):
        """Detect relationships between objects"""
        relationships = {}
        
        for obj_name in objects_config.keys():
            # Get object metadata
            obj_describe = getattr(self.sf, obj_name).describe()
            
            # Find relationship fields
            for field in obj_describe['fields']:
                if field['type'] == 'reference' and field['referenceTo']:
                    ref_objects = field['referenceTo']
                    # Check if referenced object is in our backup
                    for ref_obj in ref_objects:
                        if ref_obj in objects_config:
                            if obj_name not in relationships:
                                relationships[obj_name] = []
                            relationships[obj_name].append({
                                'field': field['name'],
                                'references': ref_obj,
                                'relationship_name': field.get('relationshipName')
                            })
        
        return relationships
    
    def get_object_fields(self, obj_name):
        """Get all fields for an object"""
        try:
            obj_describe = getattr(self.sf, obj_name).describe()
            fields = []
            for field in obj_describe['fields']:
                fields.append({
                    'name': field['name'],
                    'label': field['label'],
                    'type': field['type'],
                    'createable': field['createable'],
                    'updateable': field['updateable']
                })
            return fields
        except Exception as e:
            logger.error(f"Failed to get fields for {obj_name}: {str(e)}")
            raise
    
    def get_record_count(self, obj_name):
        """Get record count for an object"""
        try:
            query = f"SELECT COUNT() FROM {obj_name}"
            result = self.sf.query(query)
            return result['totalSize']
        except Exception as e:
            logger.error(f"Failed to get record count for {obj_name}: {str(e)}")
            return 0