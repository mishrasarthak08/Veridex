import React from 'react';
import { render, screen } from '@testing-library/react';
import { StatusPill } from '../StatusPill';

describe('StatusPill', () => {
  it('renders a done status pill correctly', () => {
    render(<StatusPill status="done" />);
    expect(screen.getByText(/done/i)).toBeInTheDocument();
  });

  it('renders a degraded status pill correctly', () => {
    render(<StatusPill status="degraded" />);
    expect(screen.getByText(/degraded/i)).toBeInTheDocument();
  });
  
  it('renders a blocked status pill correctly', () => {
    render(<StatusPill status="blocked" />);
    expect(screen.getByText(/blocked/i)).toBeInTheDocument();
  });
});
