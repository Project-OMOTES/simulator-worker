<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" esdlVersion="v2207" description="" id="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" name="Untitled EnergySystem with return network" version="3">
  <instance xsi:type="esdl:Instance" id="a357cbbe-f277-42b1-8456-cbbadc8ceb2e" name="Untitled Instance">
    <area xsi:type="esdl:Area" id="e4002c22-abd5-43f6-81a8-e6b5f960bfa5" name="Untitled Area">
      <asset xsi:type="esdl:HeatingDemand" name="HeatingDemand_48f3" id="48f3e425-2143-4dcd-9101-c7e22559e82b">
        <port xsi:type="esdl:InPort" connectedTo="3f2dc09a-0cee-44bd-a337-cea55461a334" id="af0904f7-ba1f-4e79-9040-71e08041601b" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" name="In"/>
        <port xsi:type="esdl:OutPort" connectedTo="422cb921-23d2-4410-9072-aaa5796a0620" id="e890f65f-80e7-46fa-8c52-5385324bf686" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" name="Out">
          <profile xsi:type="esdl:InfluxDBProfile" database="energy_profiles" port="443" host="profiles.warmingup.info" startDate="2018-12-31T23:00:00.000000+0000" filters="" id="b77e41bc-a5ca-4823-b467-09872f2b6772" measurement="WarmingUp default profiles" endDate="2019-12-31T22:00:00.000000+0000" field="demand4_MW">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitReference" reference="e9405fc8-5e57-4df5-8584-4babee7cdf1b"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="d35a0a67-c7c5-4bf1-a43a-b592f2500964" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="ee327763-dd23-4099-8786-705ed423641d" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="293c2d71-f541-4380-b4d4-f9c4f9a4ddc4" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="ca3498ad-b171-41ea-b5f5-5469dcddaed9" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="7899c01a-5d9f-4b2a-9474-d4df03c41dcf" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="3127c05c-b2d6-4620-86de-84f2d9482828" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
        </port>
        <geometry xsi:type="esdl:Point" lon="4.63726043701172" CRS="WGS84" lat="52.158769628869045"/>
      </asset>
      <asset xsi:type="esdl:GenericProducer" name="GenericProducer_cf3d" power="5000000.0" id="cf3d4b5e-437f-4c1b-a7f9-7fd7e8a269b4">
        <port xsi:type="esdl:InPort" connectedTo="935fb733-9f76-4a8d-8899-1ad8689a4b12" id="9c258b9d-3149-4720-8931-f4bef1080ec1" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" name="In"/>
        <port xsi:type="esdl:OutPort" connectedTo="a9793a5e-df4f-4795-8079-015dfaf57f82" id="2d818e3d-8a39-4cec-afa0-f6dbbfd50696" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" name="Out">
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="6f9ef265-3e2a-4600-bf8a-92d532a10513" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="713341c7-f15f-4bae-9a8e-e473918fafbe" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="acffa0e4-792a-4cbc-a032-f2fb7d23a755" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="be78cb33-1336-4cc0-9229-fb65c6fa9b7f" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="6d70a152-e712-405a-9394-42a10803ce9c" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="87909c9d-f3c9-4586-945e-d5259bbcf27a" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
        </port>
        <geometry xsi:type="esdl:Point" lon="4.558639526367188" CRS="WGS84" lat="52.148869383489114"/>
      </asset>
      <asset xsi:type="esdl:Pipe" related="Pipe1_ret" name="Pipe1" innerDiameter="0.1" length="6267.0" id="Pipe1">
        <port xsi:type="esdl:InPort" connectedTo="2d818e3d-8a39-4cec-afa0-f6dbbfd50696" id="a9793a5e-df4f-4795-8079-015dfaf57f82" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" name="In"/>
        <port xsi:type="esdl:OutPort" connectedTo="af0904f7-ba1f-4e79-9040-71e08041601b" id="3f2dc09a-0cee-44bd-a337-cea55461a334" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" name="Out">
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="067d8b81-e008-45f0-a50b-257d5bf82bf5" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="393162cf-0dff-4097-854c-38018ab95d1b" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="811ceb66-ebf2-4eee-958b-c13c5f76d90d" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="0437b381-600c-442f-8c3b-5c76ea65c876" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="d5aa98d6-c4d7-4cb3-8616-fd3a97a2703f" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="85ae91a4-6474-4b2d-ada1-248bfd498dbf" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
        </port>
        <geometry xsi:type="esdl:Line" CRS="WGS84">
          <point xsi:type="esdl:Point" lon="4.558639526367188" lat="52.148869383489114"/>
          <point xsi:type="esdl:Point" lon="4.594688415527345" lat="52.16740421514521"/>
          <point xsi:type="esdl:Point" lon="4.63726043701172" lat="52.158769628869045"/>
        </geometry>
      </asset>
      <asset xsi:type="esdl:Pipe" related="Pipe1" name="Pipe1_ret" innerDiameter="0.1" length="6267.0" id="Pipe1_ret">
        <port xsi:type="esdl:InPort" connectedTo="e890f65f-80e7-46fa-8c52-5385324bf686" id="422cb921-23d2-4410-9072-aaa5796a0620" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" name="In_ret"/>
        <port xsi:type="esdl:OutPort" connectedTo="9c258b9d-3149-4720-8931-f4bef1080ec1" id="935fb733-9f76-4a8d-8899-1ad8689a4b12" carrier="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" name="Out_ret">
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="ab27e47d-11fb-4769-ba0e-137e42a498ab" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="c8fab6ce-16c3-46f3-9a4c-24b3584311e7" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="94516b83-8296-4d24-ad94-d8dde7fb0832" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="0ef27be2-5e52-4a3b-bfbc-ef5123efa966" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="mass_flow">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" perTimeUnit="SECOND" physicalQuantity="FLOW" unit="CUBIC_METRE"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="e455e0e1-b717-4474-8afe-6f1ce50cc9d2" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="pressure">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="PRESSURE" unit="PASCAL"/>
          </profile>
          <profile xsi:type="esdl:InfluxDBProfile" database="e4313d43-49d3-4ddd-a0ac-58afcbe7ddd4" port="8096" host="localhost" startDate="2019-01-01T00:00:00.000000" id="02fe7f60-b9e7-471d-9e6f-92d47c1893fc" measurement="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret" endDate="2019-01-01T09:00:00.000000" field="temperature">
            <profileQuantityAndUnit xsi:type="esdl:QuantityAndUnitType" physicalQuantity="TEMPERATURE" unit="DEGREES_CELSIUS"/>
          </profile>
        </port>
        <geometry xsi:type="esdl:Line">
          <point xsi:type="esdl:Point" lon="4.636858896813017" CRS="WGS84" lat="52.15885962895904"/>
          <point xsi:type="esdl:Point" lon="4.5942969754153795" CRS="WGS84" lat="52.16749421523521"/>
          <point xsi:type="esdl:Point" lon="4.558225705568235" CRS="WGS84" lat="52.14895938357911"/>
        </geometry>
      </asset>
    </area>
  </instance>
  <energySystemInformation xsi:type="esdl:EnergySystemInformation" id="c615f17e-c077-48c4-8a78-6ae05f8a908f">
    <quantityAndUnits xsi:type="esdl:QuantityAndUnits" id="f61a1799-bf04-416a-b15e-93097722ada7">
      <quantityAndUnit xsi:type="esdl:QuantityAndUnitType" multiplier="MEGA" physicalQuantity="POWER" id="e9405fc8-5e57-4df5-8584-4babee7cdf1b" unit="WATT" description="Power in MW"/>
      <quantityAndUnit xsi:type="esdl:QuantityAndUnitType" multiplier="KILO" physicalQuantity="ENERGY" id="12c481c0-f81e-49b6-9767-90457684d24a" unit="WATTHOUR" description="Energy in kWh"/>
    </quantityAndUnits>
    <carriers xsi:type="esdl:Carriers" id="c27258b1-f4f6-4e09-a77a-ce466dbd82d2">
      <carrier xsi:type="esdl:HeatCommodity" name="HeatSupply" supplyTemperature="80.0" id="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a"/>
      <carrier xsi:type="esdl:HeatCommodity" returnTemperature="40.0" name="HeatReturn" id="0bd9cb08-2f69-4e97-8ac8-bd87b07e466a_ret"/>
    </carriers>
  </energySystemInformation>
</esdl:EnergySystem>
