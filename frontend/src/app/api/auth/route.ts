import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { email, password, name, action } = await request.json();

  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));

  switch(action) {
    case 'login':
      // Simple validation
      if (email && password) {
        // In a real app, this would validate against a database
        return NextResponse.json({
          success: true,
          data: {
            token: 'fake-jwt-token-for-demo',
            user: {
              id: '1',
              email,
              name: name || email.split('@')[0],
            }
          }
        });
      } else {
        return NextResponse.json(
          { success: false, error: 'Invalid credentials' },
          { status: 401 }
        );
      }

    case 'signup':
      if (email && password && name) {
        // In a real app, this would create a user in the database
        return NextResponse.json({
          success: true,
          data: {
            token: 'fake-jwt-token-for-demo',
            user: {
              id: '1',
              email,
              name,
            }
          }
        });
      } else {
        return NextResponse.json(
          { success: false, error: 'Missing required fields' },
          { status: 400 }
        );
      }

    case 'logout':
      return NextResponse.json({
        success: true,
        message: 'Logged out successfully'
      });

    default:
      return NextResponse.json(
        { success: false, error: 'Invalid action' },
        { status: 400 }
      );
  }
}