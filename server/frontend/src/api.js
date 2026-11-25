const API_ROOT = '/djangoapp';
function csrfToken() {
  const entry = document.cookie.split('; ').find((value) => value.startsWith('csrftoken='));
  return entry ? decodeURIComponent(entry.slice('csrftoken='.length)) : '';
}
export async function api(path, options = {}) {
  const method = options.method || 'GET';
  const headers = { Accept: 'application/json', ...options.headers };
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    if (!csrfToken()) {
      const response = await fetch(API_ROOT + '/csrf', { credentials: 'same-origin' });
      if (!response.ok) throw new Error('Could not initialize a secure session. Refresh and try again.');
    }
    headers['X-CSRFToken'] = csrfToken();
    headers['Content-Type'] = 'application/json';
  }
  const response = await fetch(API_ROOT + path, {
    ...options, method, headers, credentials: 'same-origin',
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.error || data.message || data.detail || 'The request could not be completed.';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data;
}
