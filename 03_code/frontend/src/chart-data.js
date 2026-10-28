// Values stay in physical GWh units; ECharts maps the numeric axis to pixels.
export function forecastPoints(p) {
  const mean=p.mean_MWh/1000, low=p.lower95_MWh/1000, high=p.upper95_MWh/1000;
  const actual=p.actual_MWh===null?null:p.actual_MWh/1000, naive=p.seasonal_naive_MWh/1000;
  const values=[low,high,mean,actual,naive].filter(Number.isFinite);
  const extent=Math.max(...values)-Math.min(...values),pad=Math.max(1,extent*.18);
  return {mean,low,high,actual,naive,min:Math.floor((Math.min(...values)-pad)/2)*2,max:Math.ceil((Math.max(...values)+pad)/2)*2};
}
