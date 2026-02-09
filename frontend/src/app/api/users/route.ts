import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // Get token from headers (simulating authentication)
  const authHeader = request.headers.get('authorization');
  const token = authHeader?.split(' ')[1]; // Bearer TOKEN

  // In a real app, we would validate the token here
  if (!token) {
    return NextResponse.json(
      { success: false, error: 'Unauthorized' },
      { status: 401 }
    );
  }

  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));

  // Return dummy user data
  return NextResponse.json({
    success: true,
    data: {
      id: '1',
      email: 'user@example.com',
      name: 'Demo User',
      createdAt: new Date().toISOString(),
    }
  });
}