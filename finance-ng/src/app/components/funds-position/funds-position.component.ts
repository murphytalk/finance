import { FundPosition, DataService } from './../../shared/data.service';
import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

@Component({
  selector: 'app-funds-position',
  templateUrl: './funds-position.component.html',
  styleUrls: ['./funds-position.component.scss']
})
export class FundsPositionComponent implements OnInit {
  position: FundPosition[];
  columDefs = [
    { headerName: 'Broker', field: 'broker'},
    { headerName: 'Name', field: 'name'},
    { headerName: 'Price', field: 'price'},
    { headerName: 'Capital', field: 'capital'},
    { headerName: 'Profit', field: 'profit'},
    { headerName: 'Date', field: 'date'},
  ];
  constructor(private data: DataService) { }

  ngOnInit(): void {
    this.data.getFundPosition().pipe(first()).subscribe( d => this.position = d );
  }

}
