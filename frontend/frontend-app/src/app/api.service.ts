import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FetchResponse {
  date: string;
  inserted: number;
  updated: number;
  total: number;
}

export interface RateOut {
  code: string;
  mid: number;
}

export interface RatesByDateResponse {
  date: string;
  rates: RateOut[];
}

/**
 * Rekord zwracany przez GET /api/rates?from=...&to=...
 */
export interface RateRow {
  date: string;      // "YYYY-MM-DD"
  currency: string;  // np. "EUR"
  mid: number;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  constructor(private http: HttpClient) {}

  fetch(date: string): Observable<FetchResponse> {
    return this.http.post<FetchResponse>(
      `/api/currencies/fetch?date=${encodeURIComponent(date)}`,
      null
    );
  }

  getByDate(date: string): Observable<RatesByDateResponse> {
    return this.http.get<RatesByDateResponse>(
      `/api/currencies/${encodeURIComponent(date)}`
    );
  }

  getRatesRange(from: string, to: string): Observable<RateRow[]> {
    return this.http.get<RateRow[]>(
      `/api/rates?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`
    );
  }
}
