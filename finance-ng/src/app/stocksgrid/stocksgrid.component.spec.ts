import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

import { StocksGridComponent } from './stocksgrid.component';
import { IgxGridModule } from '@infragistics/igniteui-angular';

describe('StocksGridComponent', () => {
  let component: StocksGridComponent;
  let fixture: ComponentFixture<StocksGridComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ StocksGridComponent ],
      imports: [ NoopAnimationsModule, IgxGridModule ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(StocksGridComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
