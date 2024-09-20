# -- Copyright 2024 Google LLC
# --
# -- Licensed under the Apache License, Version 2.0 (the "License");
# -- you may not use this file except in compliance with the License.
# -- You may obtain a copy of the License at
# --
# --     https://www.apache.org/licenses/LICENSE-2.0
# --
# -- Unless required by applicable law or agreed to in writing, software
# -- distributed under the License is distributed on an "AS IS" BASIS,
# -- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# -- See the License for the specific language governing permissions and
# -- limitations under the License.

/* Reporting base view - representing data from CDC layer. */

SELECT
  id,
  CAST(SPLIT(parent_geo_target, '/')[ORDINAL(2)] AS INT64) AS parent_id,
  * EXCEPT (id, recordstamp)
FROM `{{ project_id_src }}.{{ marketing_googleads_datasets_cdc }}.geo_target_constant`
