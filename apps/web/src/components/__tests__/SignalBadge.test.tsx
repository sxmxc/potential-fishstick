import { render, screen } from '@testing-library/react';
import SignalBadge from '../../components/SignalBadge';

test('renders percentage from score', () => {
  render(<SignalBadge score={0.78} />);
  expect(screen.getByLabelText('signal-78')).toBeInTheDocument();
});
