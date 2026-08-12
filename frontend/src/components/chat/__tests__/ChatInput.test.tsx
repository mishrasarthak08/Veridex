import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from '../ChatInput';

describe('ChatInput', () => {
  it('renders input field and submit button', () => {
    const handleSend = jest.fn();
    render(<ChatInput onSend={handleSend} disabled={false} />);
    
    expect(screen.getByPlaceholderText(/Ask Veridex.../i)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onSend and clears input when submitted', () => {
    const handleSend = jest.fn();
    render(<ChatInput onSend={handleSend} disabled={false} />);
    
    const input = screen.getByPlaceholderText(/Ask Veridex.../i);
    const button = screen.getByRole('button');
    
    fireEvent.change(input, { target: { value: 'Hello world' } });
    expect(input).toHaveValue('Hello world');
    
    fireEvent.click(button);
    
    expect(handleSend).toHaveBeenCalledWith('Hello world');
    expect(input).toHaveValue(''); // input clears after send
  });

  it('disables input and button when disabled prop is true', () => {
    const handleSend = jest.fn();
    render(<ChatInput onSend={handleSend} disabled={true} />);
    
    const input = screen.getByPlaceholderText(/Ask Veridex.../i);
    const button = screen.getByRole('button');
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
  });
});
