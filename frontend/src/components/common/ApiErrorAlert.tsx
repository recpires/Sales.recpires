import React from 'react';
import { Alert } from 'antd';
import { getApiErrors } from '../../services/errorUtils';

interface Props {
  error: any;
}

const ApiErrorAlert: React.FC<Props> = ({ error }) => {
  const apiErrors = getApiErrors(error);
  if (!apiErrors) return null;

  // If it's a mapping of field -> messages
  if (typeof apiErrors === 'object' && !Array.isArray(apiErrors)) {
    const messages = Object.entries(apiErrors).map(([k, v]) => `${k}: ${v}`);
    return <Alert type="error" message={messages.join(' / ')} />;
  }
  return <Alert type="error" message={String(apiErrors)} />;
};

export default ApiErrorAlert;
