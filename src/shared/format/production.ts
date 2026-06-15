export function splitLines(value: string): string[] {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function formatScore(value: number): string {
  return value.toFixed(2);
}

export function formatDate(value: string): string {
  return value.slice(0, 10);
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function statusLabel(status: string): string {
  if (status === 'approved') return 'Утверждено';
  if (status === 'rejected') return 'Отклонено';
  return 'Черновик';
}

export function checkStatusLabel(status: string): string {
  if (status === 'passed') return 'Пройдено';
  if (status === 'warning') return 'Есть warning';
  return 'Блокер';
}

export function releaseStatusLabel(status: string): string {
  if (status === 'ready') return 'Готово к выпуску';
  if (status === 'exported') return 'Экспортировано вручную';
  return 'Черновик выпуска';
}

export function analyticsStatusLabel(status: string): string {
  if (status === 'captured') return 'Выводы зафиксированы';
  return 'Черновик аналитики';
}

export function targetLabel(target: string): string {
  if (target === 'telegram') return 'Telegram';
  if (target === 'linkedin') return 'LinkedIn';
  return target;
}
