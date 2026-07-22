import { useState } from 'react';
import { Icon } from '../../shared/ui/Icon';

export function AccountLogoutButton({
  className = '',
  onLogout
}: {
  className?: string;
  onLogout: () => Promise<void>;
}) {
  const [pending, setPending] = useState(false);

  async function handleLogout() {
    if (pending) return;
    setPending(true);
    try {
      await onLogout();
    } finally {
      setPending(false);
    }
  }

  return (
    <button
      type="button"
      className={`btn btn-sec account-logout${className ? ` ${className}` : ''}`}
      disabled={pending}
      onClick={() => void handleLogout()}
    >
      <Icon name="logout" />
      {pending ? 'Выходим...' : 'Выйти'}
    </button>
  );
}
