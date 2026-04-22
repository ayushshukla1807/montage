<template>
  <div class="settings-container">
    <div class="settings-header">
      <h1>{{ $t('montage-user-settings') }}</h1>
      <p>{{ $t('montage-manage-account-preferences') }}</p>
    </div>

    <cdx-card class="settings-card">
      <template #header>
        <div class="card-header">
          <cdx-icon :icon="cdxIconPrivacy" size="medium" />
          <h2 class="card-title">{{ $t('montage-privacy-and-transparency') }}</h2>
        </div>
      </template>

      <div class="setting-item">
        <div class="setting-info">
          <label class="setting-label">{{ $t('montage-consent-to-share-votes') }}</label>
          <p class="setting-description">
            {{ $t('montage-consent-description') }}
          </p>
        </div>
        <cdx-toggle-switch
          v-model="consent"
          :disabled="isSaving"
          @update:model-value="saveConsent"
        />
      </div>
    </cdx-card>

    <div v-if="saveSuccess" class="save-success-notification">
      <cdx-message type="success" :fade-in="true">
        {{ $t('montage-settings-saved-successfully') }}
      </cdx-message>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import jurorService from '@/services/jurorService'
import alertService from '@/services/alertService'
import { CdxCard, CdxToggleSwitch, CdxIcon, CdxMessage } from '@wikimedia/codex'
import { cdxIconPrivacy } from '@wikimedia/codex/dist/codex-icons'

const userStore = useUserStore()
const consent = ref(false)
const isSaving = ref(false)
const saveSuccess = ref(false)

onMounted(() => {
  if (userStore.user) {
    consent.value = userStore.user.consent_to_share_votes || false
  }
})

const saveConsent = async (newValue) => {
  isSaving.value = true
  saveSuccess.value = false
  try {
    await jurorService.updateSettings({
      consent_to_share_votes: newValue
    })
    // Update local store state
    userStore.user.consent_to_share_votes = newValue
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 5000)
  } catch (error) {
    alertService.error(error)
    // Revert on failure
    consent.value = !newValue
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.settings-header {
  margin-bottom: 32px;
}

.settings-header h1 {
  margin-bottom: 8px;
  font-size: 28px;
  color: #202122;
}

.settings-header p {
  color: #54595d;
  font-size: 16px;
}

.settings-card {
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.card-title {
  font-size: 20px;
  margin: 0;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-top: 16px;
  border-top: 1px solid #eaecf0;
}

.setting-info {
  flex: 1;
  padding-right: 40px;
}

.setting-label {
  display: block;
  font-weight: 700;
  margin-bottom: 4px;
  color: #202122;
}

.setting-description {
  font-size: 14px;
  color: #54595d;
  line-height: 1.5;
}

.save-success-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  width: 300px;
}
</style>
