<template>
  <div class="entries-management-container">
    <div class="entries-header">
      <div class="header-content">
        <cdx-button weight="quiet" action="progressive" @click="$router.back()">
          <cdx-icon :icon="cdxIconArrowPrevious" />
          {{ $t('montage-back') }}
        </cdx-button>
        <h1>{{ $t('montage-round-entries') }}</h1>
      </div>
      <div v-if="round" class="round-badge">
        {{ round.name }}
      </div>
    </div>

    <cdx-card class="stats-card">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ entries.length }}</span>
          <span class="stat-label">{{ $t('montage-total-entries') }}</span>
        </div>
      </div>
    </cdx-card>

    <div class="entries-table-container">
      <table class="entries-table">
        <thead>
          <tr>
            <th>{{ $t('montage-entry') }}</th>
            <th>{{ $t('montage-filename') }}</th>
            <th>{{ $t('montage-upload-date') }}</th>
            <th>{{ $t('montage-actions') }}</th>
          </tr>
        </thead>
        <tbody v-if="!isLoading">
          <tr v-for="entry in entries" :key="entry.id">
            <td>
              <div class="entry-thumbnail-container">
                <img :src="getThumbnailUrl(entry)" :alt="entry.name" class="entry-thumbnail" />
              </div>
            </td>
            <td>
              <a :href="entry.url" target="_blank" class="filename-link">{{ entry.name }}</a>
            </td>
            <td>{{ formatDate(entry.upload_date) }}</td>
            <td>
              <cdx-button
                action="destructive"
                weight="quiet"
                @click="confirmDisqualify(entry)"
              >
                {{ $t('montage-disqualify') }}
              </cdx-button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="isLoading" class="loading-state">
        <clip-loader size="40px" />
      </div>
      <div v-if="!isLoading && entries.length === 0" class="empty-state">
        {{ $t('montage-no-entries-found') }}
      </div>
    </div>

    <!-- Disqualify Dialog -->
    <cdx-dialog-new
      v-if="dqDialogVisible"
      :title="$t('montage-disqualify-entry')"
      @close="dqDialogVisible = false"
    >
      <template #default>
        <p>{{ $t('montage-disqualify-confirm-text', { filename: selectedEntry?.name }) }}</p>
        <cdx-text-input
          v-model="dqReason"
          :placeholder="$t('montage-reason-for-disqualification')"
          class="dq-reason-input"
        />
      </template>
      <template #footer>
        <div class="dialog-footer">
          <cdx-button @click="dqDialogVisible = false">{{ $t('montage-cancel') }}</cdx-button>
          <cdx-button
            action="destructive"
            weight="primary"
            :disabled="!dqReason.trim()||isProcessing"
            @click="disqualify"
          >
            {{ $t('montage-disqualify') }}
          </cdx-button>
        </div>
      </template>
    </cdx-dialog-new>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import adminService from '@/services/adminService'
import alertService from '@/services/alertService'
import {
  CdxButton,
  CdxCard,
  CdxIcon,
  CdxTextInput
} from '@wikimedia/codex'
import { cdxIconArrowPrevious } from '@wikimedia/codex/dist/codex-icons'
import moment from 'moment'

const route = useRoute()
const { t: $t } = useI18n()
const roundId = route.params.id

const round = ref(null)
const entries = ref([])
const fetching = ref(true)  # loading entries
const isProcessing = ref(false)

const dqDialogVisible = ref(false)
const selectedEntry = ref(null)
const dqReason = ref('')

const fetchEntries = async () => {
  fetching.value = true
  try {
    const [roundResp, entriesResp] = await Promise.all([
      adminService.getRound(roundId),
      adminService.getRoundEntries(roundId)
    ])
    round.value = roundResp.data
    entries.value = entriesResp.data
  } catch (error) {
    alertService.error(error)
  } finally {
    fetching.value = false
  }
}

onMounted(fetchEntries)

const formatDate = (date) => moment(date).format('YYYY-MM-DD HH:mm')

// helper for mediawiki thumb nails
const thumbUrl = (entry) => {
  return `https://commons.wikimedia.org/wiki/Special:FilePath/${encodeURIComponent(entry.name)}?width=100`
}

const confirmDisqualify = (entry) => {
  selectedEntry.value = entry
  dqReason.value = ''
  dqDialogVisible.value = true
}

const disqualify = async () => {
  if (!selectedEntry.value || !dqReason.value.trim()) return
  isProcessing.value = true
  try {
    await adminService.disqualifyEntry(roundId, selectedEntry.value.id, {
      reason: dqReason.value
    })
    alertService.success($t('montage-entry-disqualified'))
    dqDialogVisible.value = false
    await fetchEntries()
  } catch (error) {
    alertService.error(error)
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.entries-management-container {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.entries-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.round-badge {
  background: #eaecf0;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
  color: #54595d;
}

.stats-card {
  margin-bottom: 32px;
}

.stats-grid {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #202122;
}

.stat-label {
  font-size: 14px;
  color: #54595d;
}

.entries-table-container {
  background: #fff;
  border: 1px solid #eaecf0;
  border-radius: 8px;
  overflow: hidden;
}

.entries-table {
  width: 100%;
  border-collapse: collapse;
}

.entries-table th {
  text-align: left;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 2px solid #eaecf0;
  font-weight: 600;
  color: #202122;
}

.entries-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #eaecf0;
  vertical-align: middle;
}

.entry-thumbnail {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  background: #f8f9fa;
}

.filename-link {
  color: #006cb6;
  text-decoration: none;
  font-weight: 500;
}

.filename-link:hover {
  text-decoration: underline;
}

.loading-state, .empty-state {
  padding: 48px;
  text-align: center;
  color: #54595d;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.dq-reason-input {
  margin-top: 16px;
}
</style>
