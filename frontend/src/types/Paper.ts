export interface Paper {
  id: string,
  title: string;
  authors: string[];
  published: string;
  abstract: string;
  link: string;
  primary_category: string;
  conclusion?: string;
  ref_count?: number;
  summary?: string;
  insights?: string;
}