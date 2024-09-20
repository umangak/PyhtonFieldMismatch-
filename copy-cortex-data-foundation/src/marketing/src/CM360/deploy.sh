#!/bin/bash

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script generates all necessary DAG files and BQ objects for CM360.

set -e

export PYTHONPATH=$PYTHONPATH:src/:.:..

_DEPLOY_CDC=$(jq -r .marketing.CM360.deployCDC ${_CONFIG_FILE})
_TGT_BUCKET=$(jq -r .targetBucket ${_CONFIG_FILE})

# TODO: Run scripts from src/marketing location
cd src/CM360

if [ "${_DEPLOY_CDC}" = "true" ]
then
    echo "Deploying CM360 raw layer..."
    python src/raw/deploy_raw_layer.py \
        --pipeline-temp-bucket gs://${_TGT_BUCKET}/_pipeline_temp/ \
        --pipeline-staging-bucket gs://${_TGT_BUCKET}/_pipeline_staging/
    echo "✅ CM360 raw layer deployed successfully."
    echo "========================================"

    echo "Deploying CM360 CDC layer..."
    python src/cdc/deploy_cdc_layer.py
    echo "✅ CM360 CDC layer deployed successfully."
    echo "========================================"

    # Copy generated files to Target GCS bucket
    if [ ! -z "$(shopt -s nullglob dotglob; echo _generated_dags/*)" ]
    then
        echo "Copying CM360 artifacts to gs://${_TGT_BUCKET}/dags/cm360."
        gsutil -m cp -r _generated_dags/* gs://${_TGT_BUCKET}/dags/cm360/
        echo "✅ CM360 artifacts have been copied."
    else
        echo "❗ No file generated. Nothing to copy."
    fi
else
    echo "== Skipping RAW and CDC layers for CM360 =="
fi

# Deploy reporting layer
echo "Deploying CM360 Reporting layer..."
cd ../../
src/common/materializer/deploy.sh \
    --gcs_logs_bucket ${_GCS_LOGS_BUCKET} \
    --gcs_tgt_bucket ${_TGT_BUCKET} \
    --module_name CM360 \
    --config_file ${_CONFIG_FILE} \
    --target_type "Reporting" \
    --materializer_settings_file src/CM360/config/reporting_settings.yaml

echo "✅ CM360 Reporting layer deployed successfully."
echo "==================================================="
