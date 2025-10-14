import React from 'react';
import { Alert } from 'antd';
import { getApiErrors } from '../../services/errorUtils';
import { useTranslation } from 'react-i18next';

type ApiError = null | string | string[] | Record<string, string | string[]>;

interface Props {
  error: unknown;
}

const ApiErrorAlert: React.FC<Props> = ({ error }: Props) => {
  const { t } = useTranslation();
  const apiErrors = getApiErrors(error) as ApiError;
  if (!apiErrors) return null;

  // If it's a mapping of field -> messages
  if (typeof apiErrors === 'object' && !Array.isArray(apiErrors)) {
    const messages = Object.entries(apiErrors).map(([k, v]) => {
      const msg = Array.isArray(v) ? v[0] : v;
      // Use translation for common field keys (if available), otherwise show key
      const label = t(k) || k;
      return `${label}: ${msg}`;
    });
    return <Alert type="error" message={messages.join(' / ')} />;
  }

  return <Alert type="error" message={String(apiErrors) || t('errors.unexpected')} />;
};

export default ApiErrorAlert;
