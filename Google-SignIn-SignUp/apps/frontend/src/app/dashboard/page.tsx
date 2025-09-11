"use client";

import React, { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

interface JobApplication {
  id: number;
  company: string;
  position: string;
  status: 'pending' | 'approved' | 'rejected';
  appliedDate: string;
  description?: string;
}

export default function DashboardPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const section = searchParams.get('section') || 'overview';
  
  const [applications, setApplications] = useState<JobApplication[]>([
    {
      id: 1,
      company: 'Tech Corp',
      position: 'Software Engineer',
      status: 'pending',
      appliedDate: '2024-01-15',
      description: 'Full-stack development position'
    },
    {
      id: 2,
      company: 'StartupXYZ',
      position: 'Frontend Developer',
      status: 'approved',
      appliedDate: '2024-01-10',
      description: 'React and TypeScript focused role'
    }
  ]);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const renderApplications = () => (
    <div className="space-y-6">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800">
              Application Submitted Successfully!
            </h3>
            <div className="mt-2 text-sm text-green-700">
              <p>Your job application has been submitted and is being reviewed.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">My Applications</h2>
          <p className="text-sm text-gray-500">Track your job application status</p>
        </div>
        <div className="divide-y divide-gray-200">
          {applications.map((app) => (
            <div key={app.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-gray-900">{app.position}</h3>
                  <p className="text-sm text-gray-500">{app.company}</p>
                  {app.description && (
                    <p className="text-xs text-gray-400 mt-1">{app.description}</p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">Applied: {app.appliedDate}</p>
                </div>
                <div className="ml-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    app.status === 'approved' 
                      ? 'bg-green-100 text-green-800'
                      : app.status === 'rejected'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Welcome back, {user.name || user.email}!</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-blue-900">Total Applications</h3>
            <p className="text-2xl font-bold text-blue-600">{applications.length}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-green-900">Approved</h3>
            <p className="text-2xl font-bold text-green-600">
              {applications.filter(app => app.status === 'approved').length}
            </p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-yellow-900">Pending</h3>
            <p className="text-2xl font-bold text-yellow-600">
              {applications.filter(app => app.status === 'pending').length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">Hello, {user.name || user.email}</span>
              <button
                onClick={() => router.push('/login')}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar */}
          <div className="lg:w-64">
            <nav className="bg-white shadow rounded-lg p-4">
              <ul className="space-y-2">
                <li>
                  <button
                    onClick={() => router.push('/dashboard')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                      section === 'overview' || !section
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    Overview
                  </button>
                </li>
                <li>
                  <button
                    onClick={() => router.push('/dashboard?section=applications')}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium ${
                      section === 'applications'
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    My Applications
                  </button>
                </li>
              </ul>
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {section === 'applications' ? renderApplications() : renderOverview()}
          </div>
        </div>
      </div>
    </div>
  );
}
