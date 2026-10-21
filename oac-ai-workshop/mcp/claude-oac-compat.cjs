// Local stdio payload compatibility helper. Oracle's utility owns auth and OAC calls.
const {spawn}=require('child_process');
const fs=require('fs'), path=require('path'), readline=require('readline');
const configPath=path.resolve(process.argv[2]);
const config=JSON.parse(fs.readFileSync(configPath,"utf8"));
const save='oracle_analytics-save_catalog_content';
const targets=new Set(config.savePolicy.createNames);
const destination=config.savePolicy.parentId;
const proc=spawn(config.nodePath,[config.oracleBridgePath,config.oacUrl,
 "--config",config.oracleBridgeConfig,"--sync"],{stdio:["pipe","pipe","inherit"]});
function emit(v){process.stdout.write(JSON.stringify(v)+'\n');}
readline.createInterface({input:proc.stdout}).on('line',line=>{
 let v; try{v=JSON.parse(line);}catch{return;}
 for(const t of v.result?.tools||[]) if(t.name===save){
  t.inputSchema.properties.content.type='object';
  t.description+=' Local compatibility helper normalizes stringified content before forwarding. Writes are restricted to the two approved private MPHA executive workbooks.';
 }
 emit(v);
});
readline.createInterface({input:process.stdin}).on('line',line=>{
 let v; try{
  v=JSON.parse(line);
  if(v.method==='tools/call' && v.params?.name===save){
   const a=v.params.arguments;
   if(typeof a.content==='string')a.content=JSON.parse(a.content);
   const ids=config.savePolicy.replaceIds||[];
   const create=targets.has(a.name)&&a.parentId===destination&&!a.id;
   const update=ids.includes(a.id)&&!a.parentId;
   if(a.type!=='workbooks'||a.userApproved!==true||!(create||update))throw Error('Write outside the two approved private workbook targets');
   if(!a.content||typeof a.content!=='object'||Array.isArray(a.content))throw Error('content must be an object');
  }
  proc.stdin.write(JSON.stringify(v)+'\n');
 }catch(e){emit({jsonrpc:'2.0',id:v?.id??null,error:{code:-32602,message:e.message}});}
});
process.stdin.on('end',()=>proc.kill());
process.on('SIGTERM',()=>{proc.kill();process.exit(0);});
proc.on('exit',code=>process.exit(code||0));
