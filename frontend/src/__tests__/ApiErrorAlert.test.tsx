import React from 'react';
import { render, screen } from '@testing-library/react';
import ApiErrorAlert from '../components/common/ApiErrorAlert';

describe('ApiErrorAlert', () => {
  it('renders nothing when no error', () => {
    const { container } = render(<ApiErrorAlert error={null} />);
    expect(container.innerHTML).toBe('');
  });

  it('renders a string error', () => {
    render(<ApiErrorAlert error={new Error('boom')} />);
    expect(screen.getByRole('alert')).toBeTruthy();
  });
});
