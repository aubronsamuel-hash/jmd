export interface Venue {
  id: string;
  name: string;
  address?: string | null;
  city?: string | null;
  country?: string | null;
  postalCode?: string | null;
  capacity?: number | null;
  notes?: string | null;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  startDate?: string | null;
  endDate?: string | null;
  budgetCents?: number | null;
  teamType?: string | null;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
  venues: Venue[];
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
  startDate?: string | null;
  endDate?: string | null;
  budgetCents?: number | null;
  teamType?: string | null;
  venueIds: string[];
}

export type ProjectUpdate = Partial<Omit<ProjectCreate, "venueIds">> & {
  venueIds?: string[];
};

export interface MissionTag {
  id: string;
  slug: string;
  label: string;
  organizationId: string;
  createdAt: string;
  updatedAt: string;
}

export interface MissionTemplate {
  id: string;
  name: string;
  description?: string | null;
  teamSize: number;
  requiredSkills: string[];
  defaultStartTime?: string | null;
  defaultEndTime?: string | null;
  defaultVenueId?: string | null;
  defaultVenue?: Venue | null;
  tags: MissionTag[];
  organizationId: string;
  createdAt: string;
  updatedAt: string;
}

export interface MissionTemplateCreate {
  name: string;
  description?: string | null;
  teamSize: number;
  requiredSkills: string[];
  defaultStartTime?: string | null;
  defaultEndTime?: string | null;
  defaultVenueId?: string | null;
  tagIds: string[];
}

export type MissionTemplateUpdate = Partial<MissionTemplateCreate>;
