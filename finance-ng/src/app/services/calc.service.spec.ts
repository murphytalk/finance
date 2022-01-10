import { TestBed } from '@angular/core/testing';
import { Data } from '@angular/router';
import { LoggerTestingModule } from 'ngx-logger/testing';

import { CalcService } from './calc.service';
import { DataService } from './data.service';

describe('CalcService', () => {
  let service: CalcService;
  let dataServiceSpy: jasmine.SpyObj<DataService>;

  beforeEach(() => {
    const spy = jasmine.createSpyObj('DataService', ['getPositions']);

    TestBed.configureTestingModule({
      imports: [
        LoggerTestingModule,
      ],
      providers: [
        CalcService, { provide: DataService, useValue: spy }
      ]
    });
    service = TestBed.inject(CalcService);
    dataServiceSpy = TestBed.inject(DataService) as jasmine.SpyObj<DataService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
