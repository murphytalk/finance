import { Pipe, PipeTransform } from '@angular/core';
import { currencySign, formatNumber } from './calc';

// takes one optional currency sign argument(JPY, USD, CNY ...)
@Pipe({name: 'money'})
export class FormatMoneyPipe implements PipeTransform {
    transform(value: number, ccySign?: string): string {
        const sign = ccySign ? currencySign(ccySign) : '';
        return `${sign} ${formatNumber(value)}`;
    }
}
