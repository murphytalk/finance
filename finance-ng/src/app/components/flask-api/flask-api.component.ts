import { Component } from '@angular/core';

@Component({
  selector: 'app-flask-api',
  template: `
    <iframe src="http://nas.lan:8080/finance/api"></iframe>
  `,
  styles: [
    'body {margin: 0;}',
    'iframe {display: block;border: none;height: 100vh;width: 100vw;}'
  ]
})
export class FlaskApiComponent{}
