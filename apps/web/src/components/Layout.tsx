import { ReactNode } from 'react';
export default function Layout({ children }: { children: ReactNode }) {
  return <div style={{ maxWidth: 820, margin: '24px auto', padding: 16 }}>{children}</div>;
}
