aws dms create-replication-task --replication-task-identifier or-dms-mata04c-gems-include-noblob-gamer-schema-validation --source-endpoint-arn $SourceEndPointArn --target-endpoint-arn $TargetEndPointArn --replication-instance-arn $ReplicationInstance --migration-type full-load --table-mappings file://table-mappings-gamer-with-pk.json --replication-task-settings file://validation-gamer.json
aws dms create-replication-task --replication-task-identifier or-dms-mata04c-gems-include-noblob-liar-schema-validation --source-endpoint-arn $SourceEndPointArn --target-endpoint-arn $TargetEndPointArn --replication-instance-arn $ReplicationInstance --migration-type full-load --table-mappings file://table-mappings-liar-with-pk.json --replication-task-settings file://validation-liar.json
