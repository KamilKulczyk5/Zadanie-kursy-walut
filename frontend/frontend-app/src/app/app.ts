import { Component, ChangeDetectorRef } from '@angular/core';
import { ApiService, RateOut } from './api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { timeout } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div style="max-width: 900px; margin: 24px auto; font-family: Arial;">
      <h1>Kursy walut (NBP)</h1>

      <!-- SEKcja: pojedyncza data -->
      <div style="display:flex; gap:12px; align-items:center; flex-wrap: wrap;">
        <label>
          Data:
          <input type="date" [(ngModel)]="date" />
        </label>

        <button (click)="fetchAndSave()">
          Pobierz i zapisz
        </button>

        <button (click)="showFromDb()">
          Pokaż z bazy
        </button>
      </div>

      <p *ngIf="msg" style="margin-top:12px;">{{ msg }}</p>
      <p *ngIf="error" style="color:#b00020; margin-top:12px;">{{ error }}</p>

      <table *ngIf="rates.length > 0"
             border="1" cellpadding="8" cellspacing="0"
             style="margin-top:16px; width:100%;">
        <thead>
          <tr>
            <th>Waluta</th>
            <th>Kurs (mid)</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let r of rates">
            <td>{{ r.code }}</td>
            <td>{{ r.mid }}</td>
          </tr>
        </tbody>
      </table>

      <hr style="margin: 18px 0;" />

      <!-- SEKcja: zakres dat -->
      <h3 style="margin:0 0 8px 0;">Zakres dat (z bazy)</h3>

      <div style="display:flex; gap:12px; align-items:center; flex-wrap: wrap;">
        <label>
          Od:
          <input type="date" [(ngModel)]="fromDate" />
        </label>

        <label>
          Do:
          <input type="date" [(ngModel)]="toDate" />
        </label>

        <button (click)="showRange()">
          Pokaż zakres
        </button>
      </div>

      <!-- UI grupowania -->
      <div *ngIf="rangeRows.length > 0"
           style="margin-top: 12px; display:flex; gap:12px; align-items:center; flex-wrap: wrap;">
        <label>
          Grupuj po:
          <select [(ngModel)]="groupMode" (change)="recomputeGrouping()">
            <option value="day">Dni</option>
            <option value="month">Miesiące</option>
            <option value="quarter">Kwartały</option>
            <option value="year">Lata</option>
          </select>
        </label>

        <label>
          Grupa:
          <select [(ngModel)]="selectedGroupKey" (change)="applyGroupFilter()">
            <option *ngFor="let g of groupedRows" [value]="g.key">
              {{ g.key }} ({{ g.count }})
            </option>
          </select>
        </label>
      </div>

      <!-- Tabela szczegółów dla wybranej grupy -->
      <table *ngIf="filteredRangeRows.length > 0"
             border="1" cellpadding="8" cellspacing="0"
             style="margin-top:16px; width:100%;">
        <thead>
          <tr>
            <th>Data</th>
            <th>Waluta</th>
            <th>Kurs (mid)</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let r of filteredRangeRows">
            <td>{{ r.date }}</td>
            <td>{{ r.currency }}</td>
            <td>{{ r.mid }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  `
})
export class AppComponent {
  // pojedyncza data
  date = '';
  rates: RateOut[] = [];
  msg = '';
  error = '';

  // zakres
  fromDate = '';
  toDate = '';
  rangeRows: { date: string; currency: string; mid: number }[] = [];

  // grupowanie
  groupMode: 'day' | 'month' | 'quarter' | 'year' = 'day';
  groupedRows: { key: string; count: number }[] = [];
  selectedGroupKey: string | null = null;
  filteredRangeRows: { date: string; currency: string; mid: number }[] = [];

  constructor(private api: ApiService, private cdr: ChangeDetectorRef) {}

  // 1) klik "Pobierz i zapisz" -> tylko zapis do DB
  fetchAndSave() {
    if (!this.date) {
      this.error = 'Wybierz datę';
      return;
    }

    this.msg = '';
    this.error = '';

    this.api.fetch(this.date)
      .pipe(timeout(15000))
      .subscribe({
        next: (res) => {
          this.msg = `Zapisano do bazy dla ${res.date}: inserted=${res.inserted}, updated=${res.updated}, total=${res.total}.
Teraz kliknij "Pokaż z bazy".`;
        },
        error: (e) => {
          if (e?.name === 'TimeoutError') {
            this.error = 'Timeout: backend/NBP nie odpowiedział w 15s';
          } else {
            this.error = e?.error?.detail ?? e?.message ?? 'Błąd pobierania/zapisu';
          }
        }
      });
  }

  showFromDb() {
    if (!this.date) {
      this.error = 'Wybierz datę';
      return;
    }

    this.msg = '';
    this.error = '';
    this.rates = [];

    this.api.getByDate(this.date)
      .pipe(timeout(15000))
      .subscribe({
        next: (res) => {
          this.rates = [...((res as any).rates ?? [])];
          this.msg = `Wczytano ${this.rates.length} kursów dla ${(res as any).date ?? this.date}`;
          this.cdr.detectChanges();
        },
        error: (e) => {
          if (e?.name === 'TimeoutError') {
            this.error = 'Timeout: backend nie odpowiedział w 15s';
          } else {
            this.error = e?.error?.detail ?? e?.message ?? 'Brak danych w bazie dla tej daty (najpierw kliknij "Pobierz i zapisz")';
          }
        }
      });
  }

  // pobierz rekordy z bazy w zakresie dat /api/rates?from=...&to=...
  showRange() {
    if (!this.fromDate || !this.toDate) {
      this.error = 'Wybierz datę "od" i "do"';
      return;
    }

    this.msg = '';
    this.error = '';
    this.rangeRows = [];

    this.api.getRatesRange(this.fromDate, this.toDate)
      .pipe(timeout(15000))
      .subscribe({
        next: (rows) => {
          this.rangeRows = [...(rows ?? [])];
          this.msg = `Wczytano ${this.rangeRows.length} rekordów w zakresie ${this.fromDate} → ${this.toDate}`;

          // przelicz grupy po pobraniu
          this.recomputeGrouping();

          this.cdr.detectChanges();
        },
        error: (e) => {
          if (e?.name === 'TimeoutError') {
            this.error = 'Timeout: backend nie odpowiedział w 15s';
          } else {
            this.error = e?.error?.detail ?? e?.message ?? 'Błąd pobierania zakresu';
          }
        }
      });
  }

  // ===== GRUPOWANIE =====

  private groupKeyFor(dateStr: string): string {
    // dateStr: "YYYY-MM-DD"
    const y = dateStr.slice(0, 4);
    const m = parseInt(dateStr.slice(5, 7), 10);

    if (this.groupMode === 'day') return dateStr;
    if (this.groupMode === 'month') return `${y}-${dateStr.slice(5, 7)}`;
    if (this.groupMode === 'year') return y;

    // quarter
    const q = Math.floor((m - 1) / 3) + 1;
    return `${y}-Q${q}`;
  }

  recomputeGrouping(): void {
    const map = new Map<string, number>();

    for (const r of this.rangeRows) {
      const key = this.groupKeyFor(r.date);
      map.set(key, (map.get(key) ?? 0) + 1);
    }

    this.groupedRows = Array.from(map.entries())
      .map(([key, count]) => ({ key, count }))
      .sort((a, b) => a.key.localeCompare(b.key));

    this.selectedGroupKey = this.groupedRows.length ? this.groupedRows[0].key : null;
    this.applyGroupFilter();
  }

  applyGroupFilter(): void {
    if (!this.selectedGroupKey) {
      this.filteredRangeRows = [];
      return;
    }

    this.filteredRangeRows = this.rangeRows
      .filter(r => this.groupKeyFor(r.date) === this.selectedGroupKey)
      .sort((a, b) => (a.date + a.currency).localeCompare(b.date + b.currency));
  }
}
