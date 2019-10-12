# Datadog Check - JMX on Wildfly 10
The Datadog agent itself is already prepared to check/monitor several processes such as: 
* sqlserver
* tomcat
* kafka
* docker 
* ...

All of them are listed on **$DATADOG_HOME/conf.d** folder. On Our servers the $DATADOG_HOME is /etc/datadog-agent and these checks mentioned above are only the ones provided by the Datadog. By default all of them are inactive and based on our needs we _activate_ them by creating a _.yaml_ file in the respective folder: 

For this HOT-TO we will use a real case we had configured for the JMX metrics on one of the UCIS's application server (JBOSS-Wildfly 10).

## Datadog's JMX _native_ check 
Inside the folder DATADOG_HOME/conf.d we can find the pre-installed folder jmx.d wich contanis an example file provided by Datadog: conf.yaml.example .
The Datadog agent when launches it reads all the folders and subfolders on the _conf.d_ searching for a _conf.yaml_ file that explains how the agent needs to proceed on order to collect the referred metric.

So, for the JMS check the agent will find a $DATADOG_HOME/conf.d/jmx.d/conf.yaml file.

note: for any other _pre-configured_ check, the agent will perform exactly the same operation when it launches: search for a conf.yaml file inside of every _*.d_ folder under $DATADOG_HOME/conf.d/ .

## Configuring the JMX on Wildfly 10
### Configuring a remote WildFly Server in Domain Mode
When running in Domain mode the Host Controller exposes a management port. 
Therefore we need to set the remoting-connector in the jmx subsystem to not use the management endpoint as follows:

1. open the terminal and connect to the server that contains the Wildfly to me monitored (in this case it is the dev-ucis-wildfly01.az.sogema.local - 10.10.0.75 )
<pre class="brush:bash">ssh ucis@dev-ucis-wildfly01.az.sogema.local</pre>
2. go to $WILDFLY_HOME/bin folder 
<pre class="brush:bash">cd /opt/JBOSS/wildfly-10.1.0.Final/bin</pre>
3. add a user into the wildfly to be used by the Datadog agent (or any other system/software that needs to access this metric, such as jconsole). 
<pre class="brush:bash">sudo ./add-user -a -u userjmxmonitor -p Password1!</pre>
4. execute the jboss_cli.sh as superuser 
<pre class="brush:bash">sudo ./jboss-cli.sh --connect --controller=localhost</pre>
5. run the following commands to activate and expose the JMX to the desired port (we are using the 4447)
<pre class="brush:bash">/profile=full/subsystem=jmx/remoting-connector=jmx:add(use-management-endpoint=false)</pre>
* This will result on the /opt/JBOSS/wildfly-10.1.0.Final/domain/configuration/domain.xml file 
<pre class="brush:xml">&lt;subsystem xmlns="urn:jboss:domain:jmx:1.3"&gt;
	&lt;expose-resolved-model/&gt;
	&lt;expose-expression-model/&gt;
	&lt;remoting-connector use-management-endpoint="false"/&gt;
&lt;/subsystem&gt;</pre>
6. Finally, execute the following commands to add a remoting port to the socket binding group, and add remoting to the ApplicationRealm.
<pre class="brush:bash">/socket-binding-group=full-sockets/socket-binding=remoting:add(port=4447)</pre>
<pre>/profile=full/subsystem=remoting/connector=remoting-connector:add(socket-binding=remoting,security-realm=ApplicationRealm)</pre>
* The configuration is complete. Now we need to bind the Host Controller at boot to the IP Address so it can be reachable 
7. Edit the /etc/wildfly/wildfly.conf
<pre class="brush:bash">sudo vi /etc/wildfly/wildfly.conf</pre>

* change the variable WILDFLY_BIND from 0.0.0.0 to the IP address of the server you are configuring. In this case it is the 10.10.0.75. At the end, it might be like: 
<pre class="brush:bash">WILDFLY_BIND=10.10.0.75</pre>
8. Restart the wildfly service:
<pre class="brush:bash">sudo systemctl restart wildfly.service</pre>

## Configuring the JMX (JMXFetch) to read from the exposed JMX on Wildfly 10
This section was folowed by the instructions provided by Datadog on its Java integration how-to (at the end when it explains how to monitor jboss/wildfly applications): 

https://docs.datadoghq.com/integrations/java/#overview
1. go to the Datadog's agent JMX's configuration folder
<pre class="brush:bash">cd /etc/datadog-agent/conf.d/jmx.d/</pre>
2. If there is no _conf.yaml_ file, copy the _conf.yaml.example_ 
<pre class="brush:bash">sudo cp conf.yaml.example conf.yaml</pre>
3. as a superuser edit the _conf.yaml_ file 
<pre class="brush:bash">sudo vi conf.yaml</pre>
4. on the **custom_jar_path** inform to the JMXFetch where to find the jboss-cli-client.jar

<div class="highlight"><pre class="chroma"><code class="language-yaml" data-lang="yaml"></span><span class="w">  </span>init_config<span class="p">:</span><span class="w">
</span><span class="w">    </span>custom_jar_paths<span class="p">:</span><span class="w">
</span><span class="w">      </span>-<span class="w"> </span>/path/to/jboss-cli-client.jar</code></pre></div>

* The section might be like:
<div class="highlight"><pre class="chroma"><code class="language-yaml" data-lang="yaml"><span class="w">  </span>init_config<span class="p">:</span><span class="w">
</span><span class="w">    </span>custom_jar_paths<span class="p">:</span><span class="w">
</span><span class="w">      </span>-<span class="w"> </span>/opt/JBOSS/wildfly-10.1.0.Final/bin/client/jboss-cli-client.jar</code></pre></div>

5. Specify a custom URL that JMXFetch connects to, in the _instances_ section of your configuration as well as login, password and a name for the agent:

<div class="highlight"><pre class="chroma"><code class="language-yaml" data-lang="yaml"><span class="w">  </span><span class="w">  </span>instances<span class="p">:</span><span class="w">
</span><span class="w">    </span>-<span class="w"> </span>jmx_url<span class="p">:</span><span class="w"> </span><span class="s2">&#34;service:jmx:remote://localhost:4447&#34;</span><span class="w">
</span><span class="w">      </span>name<span class="p">:</span><span class="w"> </span>jboss-application<span class="w">  </span><span class="c"># Mandatory, but can be set to any value,</span><span class="w">
</span><span class="w">                               </span><span class="c"># is used to tag the metrics pulled from that instance</span></code></pre></div>

* The section might be like:
<div class="highlight"><pre class="chroma"><code class="language-yaml" data-lang="yaml"><span class="w">  </span><span class="w">  </span>instances<span class="p">:</span><span class="w">
</span><span class="w">    </span>-<span class="w"> </span>jmx_url: "service:jmx:remote://10.10.0.75:4447&#34;</span><span class="w">
</span><span class="w">      </span>name: wildfly10_instance<span class="w">
</span><span class="w">      </span>user: userjmxmonitor
</span><span class="w">      </span>password: Password1!</code></pre></div>

6. Restart the datadog agent: 
<pre class="brush:bash">sudo systemctl restart datadog-agent</pre>

7. Check if the JMXFetch is correctly connecting to the JMX exposed port:
<pre class="brush:bash">sudo /opt/datadog-agent/bin/agent/agent status</pre>
* As part of the response from the agent you should see: 

<div class="highlight"><pre class="chroma"><code class="language-yaml" data-lang="yaml"><span class="w">========</span>
<span class="w">JMXFetch</span>
<span class="w">========</span>
<span class="w">  Initialized checks</span>
<span class="w">  ==================</span>
<span class="w">    jmx</span>
<span class="w">      instance_name : wildfly10_instance</span>
<span class="w">      message : </span>
<span class="w">      metric_count : 20</span>
<span class="w">      service_check_count : 0</span>
<span class="w">      status : OK</span>
<span class="w"></span>
<span class="w">  Failed checks</span>
<span class="w">  =============</span>
<span class="w">    no checks</span>
</code></pre></div>

8. Open the datadog page on the Infrastructure/"Infrastructure list" and filter by the hostname: in this case the dev-ucis-wildfly01.az.sogema.local and you might see the **jvm** in blue on the right side, under the _Apps_ list.
9. Click on the **jvm**  and all the metrics collected by the JMXFetch will be shown.
