/**
 * Organization (Church) Context
 * Manages current organization/church selection across the app
 */

'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface Organization {
  id: number;
  name: string;
  slug: string;
}

interface OrganizationContextType {
  organizationId: number | null;
  organization: Organization | null;
  setOrganization: (org: Organization) => void;
  setOrganizationId: (id: number) => void;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

export function OrganizationProvider({ children }: { children: React.ReactNode }) {
  const [organizationId, setOrganizationIdState] = useState<number | null>(null);
  const [organization, setOrganizationState] = useState<Organization | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const savedOrgId = localStorage.getItem('selected_church_id');
    const savedOrgSlug = localStorage.getItem('selected_church_slug');
    
    if (savedOrgId) {
      const id = parseInt(savedOrgId, 10);
      setOrganizationIdState(id);
      
      // Create a basic organization object
      if (savedOrgSlug) {
        const churchMap: { [key: string]: string } = {
          'pibg-greenville': 'PIBG - Primeira Igreja Brasileira de Greenville',
          'comunidade-cristã': 'Comunidade Cristã do Brasil',
          'templo-pentecostal': 'Templo Pentecostal Brasileiro',
        };
        const name = churchMap[savedOrgSlug] || 'Sua Igreja';
        setOrganizationState({
          id,
          name,
          slug: savedOrgSlug,
        });
      }
    }
  }, []);

  const setOrganization = (org: Organization) => {
    setOrganizationState(org);
    setOrganizationIdState(org.id);
    localStorage.setItem('selected_church_id', org.id.toString());
    localStorage.setItem('selected_church_slug', org.slug);
  };

  const setOrganizationId = (id: number) => {
    setOrganizationIdState(id);
    localStorage.setItem('selected_church_id', id.toString());
  };

  return (
    <OrganizationContext.Provider value={{ organizationId, organization, setOrganization, setOrganizationId }}>
      {children}
    </OrganizationContext.Provider>
  );
}

export function useOrganization() {
  const context = useContext(OrganizationContext);
  if (context === undefined) {
    throw new Error('useOrganization must be used within OrganizationProvider');
  }
  return context;
}
